import os
import sqlite3

import pytest
from pytest_mock import MockerFixture

from ctest_py.plugin import CloudSqlite


# -----------------------------
# Helpers / Fixtures
# -----------------------------
class DummyCreds:
    def __init__(self, token: str = "tok"):  # minimal object for google creds
        self.token = token

    def refresh(self, request):
        pass


# -----------------------------
# Behaviors under test
# -----------------------------
# 1) __init__ should set required environment variables and load extension when creds available
# 2) __init__ should create cache directory if missing
# 3) __init__ should handle sqlite3.OperationalError during load (prints and exits)
# 4) _get_creds should raise if token is None
# 5) _run_process should construct and run subprocess with expected args
# 6) create_container/upload_db/init_db orchestration logic should perform actions as expected
# 7) destroy_db/download_db/list_files_db/list_manifest_db delegate to _run_process with proper args
# 8) create_local_db creates a sqlite file


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    # Ensure environment isolation for each test
    for k in os.environ.keys():
        if k.startswith("SQ_") or k in {"CS_KEY", "CS_ACCOUNT"}:
            os.environ.pop(k, None)
    # Keep monkeypatch for chdir - no mocker equivalent
    monkeypatch.chdir(tmp_path)
    yield


def _mock_creds(mocker: MockerFixture, token: str = "token", project: str = "proj"):
    """Mock CloudSqlite._get_creds using mocker.patch.object."""
    mocker.patch.object(
        CloudSqlite, "_get_creds", staticmethod(lambda: (token, project))
    )


def test_init_sets_env_and_loads_extension(tmp_path, mocker: MockerFixture):
    _mock_creds(mocker)

    # Mock sqlite3.connect - returns MagicMock automatically
    mock_connect = mocker.patch("sqlite3.connect")
    temp_conn = mock_connect.return_value

    cache_dir = tmp_path / "cache"
    CloudSqlite(
        bucket="bkt/path",
        vfs_name="vname",
        cache_dir=str(cache_dir),
        bucket_alias="alias",
    )

    # Env variables set
    assert os.environ["SQ_VFS_NAME"] == "vname"
    assert os.environ["SQ_CACHE_DIR"] == str(cache_dir)
    assert os.environ["SQ_DB_BUCKET"] == "bkt/path"
    assert os.environ["SQ_CONTAINER_ALIAS"] == "alias"
    assert os.environ["CS_KEY"] == "token"
    assert os.environ["CS_ACCOUNT"] == "proj"

    # Extension loaded
    temp_conn.enable_load_extension.assert_called_once_with(True)
    temp_conn.load_extension.assert_called_once()
    temp_conn.close.assert_called_once()


def test_init_creates_cache_dir(tmp_path, mocker: MockerFixture):
    _mock_creds(mocker)

    mocker.patch("sqlite3.connect")

    cache_dir = tmp_path / "sub" / "cache"
    assert not cache_dir.exists()

    CloudSqlite(bucket="b/path", cache_dir=str(cache_dir))
    assert cache_dir.exists()


def test_init_handles_extension_error(tmp_path, mocker: MockerFixture):
    _mock_creds(mocker)

    mock_connect = mocker.patch("sqlite3.connect")
    temp_conn = mock_connect.return_value
    temp_conn.load_extension.side_effect = sqlite3.OperationalError("boom")

    # Mock exit to avoid stopping pytest
    mocked_exit = mocker.patch("builtins.exit")
    CloudSqlite(bucket="b/path", cache_dir=str(tmp_path / "c"))
    mocked_exit.assert_called_once()


def test_get_creds_raises_on_missing_token(mocker: MockerFixture):
    # Patch google.auth.default and credentials.refresh
    class Creds:
        def __init__(self):
            self.token = None

        def refresh(self, request):
            self.token = None

    def fake_default():
        return Creds(), "project-x"

    mocker.patch("ctest_py.plugin.default", return_value=fake_default())
    mocker.patch("ctest_py.plugin.Request", return_value=object())

    with pytest.raises(RuntimeError):
        CloudSqlite._get_creds()


def test_run_process_invokes_subprocess(monkeypatch, mocker: MockerFixture):
    _mock_creds(mocker, token="tok", project="proj")

    mock_run = mocker.patch("ctest_py.plugin.subprocess.run")

    # Keep monkeypatch for setenv - cleaner than mocker.patch.dict
    monkeypatch.setenv("PYTHONPATH", "")

    # Mock __file__ to get deterministic path
    lib_path = __file__
    mocker.patch("ctest_py.plugin.__file__", lib_path)

    CloudSqlite._run_process("start", "-v", "--x")

    mock_run.assert_called_once()
    call_args = mock_run.call_args
    argv = call_args[0][0]  # First positional arg is the argv list
    check = call_args[1]["check"]  # check is a keyword arg

    assert argv[0].endswith("/blockcachevfsd")
    assert argv[1:5] == [
        "start",
        "-module",
        "google",
        "-user",
    ]
    # Ensure auth payload and passthrough args are present
    assert "proj" in argv
    assert "tok" in argv
    assert argv[-2:] == ["-v", "--x"]
    assert check is True


def test_init_db_and_upload_flow(tmp_path, mocker: MockerFixture):
    # Spy on create_container, upload_db, os.remove using mocker
    mock_create_container = mocker.patch.object(CloudSqlite, "create_container")
    mock_upload_db = mocker.patch.object(CloudSqlite, "upload_db")
    mock_remove = mocker.patch("os.remove")

    # Use a temp sqlite connect that records ops but works
    real_connect = sqlite3.connect

    def connect_wrap(path):
        # Return a real connection in tmp dir
        return real_connect(tmp_path / path)

    mocker.patch("sqlite3.connect", side_effect=connect_wrap)

    CloudSqlite.init_db("my.db", "gs://bucket/loc", block_size="8k")

    mock_create_container.assert_called_once_with("gs://bucket/loc", "8k")
    mock_upload_db.assert_called_once_with("gs://bucket/loc", "my.db", "my.db")
    mock_remove.assert_called_once_with("my.db")


@pytest.mark.parametrize(
    "method, args, expected",
    [
        (CloudSqlite.destroy_db, ("gs://b/path",), ["destroy", "gs://b/path"]),
        (
            CloudSqlite.download_db,
            ("gs://b/path",),
            ["download", "-container", "gs://b/path", "testing"],
        ),
        (CloudSqlite.list_files_db, ("gs://b/path",), ["list", "gs://b/path"]),
        (CloudSqlite.list_manifest_db, ("gs://b/path",), ["manifest", "gs://b/path"]),
    ],
)
def test_delegating_helpers(mocker: MockerFixture, method, args, expected):
    # Capture calls manually since we're replacing with staticmethod
    calls: list = []
    mocker.patch.object(
        CloudSqlite, "_run_process", staticmethod(lambda *av: calls.append(list(av)))
    )

    method(*args)

    assert calls and calls[0] == expected


def test_create_local_db_creates_file(tmp_path, monkeypatch):
    # Keep monkeypatch for chdir
    monkeypatch.chdir(tmp_path)
    CloudSqlite.create_local_db()
    assert (tmp_path / "example.db").exists()
