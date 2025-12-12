import os
import sqlite3
import subprocess
from functools import cache
from typing import cast

from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request


class CloudSqlite:
    """Cloud version of SQLite with Google Cloud Storage integration."""

    def __init__(
        self,
        bucket: str,
        vfs_name: str = "ssb_vfs",
        cache_dir: str = "./cache",
        bucket_alias: str = "buckets",
    ) -> None:
        """Loads the extension into sqlite.

        Can connect to the database like this:
        >>> import sqlite3
        >>> sqlite3.connect(f"file:/{bucket_alias}/{database_name}?vfs={vfs_name}", uri=True)

        Args:
            bucket: Bucket path. ex: ssb-vare-tjen-korttid-data-produkt-prod/vhi/db
            vfs_name: The vfs name used to access the extension
            cache_dir: The path to the directory used for caching. Will create the directory if it does not exists
            bucket_alias: The alias for the bucket.
        """
        access_token, project_id = CloudSqlite._get_creds()

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        os.environ["CS_KEY"] = access_token
        os.environ["CS_ACCOUNT"] = project_id
        os.environ["SQ_VFS_NAME"] = vfs_name
        os.environ["SQ_CACHE_DIR"] = cache_dir
        os.environ["SQ_DB_BUCKET"] = bucket
        os.environ["SQ_CONTAINER_ALIAS"] = bucket_alias
        os.environ["SQ_VERBOSITY"] = "0"

        lib_path = os.path.abspath(__file__)
        extension_path = os.path.dirname(lib_path) + "/libcurlcrypto.so"
        # Step 1: Load the extension using a temporary connection
        temp_conn = sqlite3.connect(":memory:")
        temp_conn.enable_load_extension(True)

        try:
            # The extension's entry point should register the 'myvfs' VFS persistently.
            temp_conn.load_extension(extension_path)
            print(f"Extension loaded successfully from {extension_path}")
        except sqlite3.OperationalError as e:
            print(f"Failed to load extension: {e}")
            temp_conn.close()
            exit()

        temp_conn.close()

    @staticmethod
    def clean_blocks() -> None:
        """Cleans up memory blocks using a C extension.

        Raises:
            NotImplementedError: If the method is called, indicating that
                further testing and implementation are required.
        """
        raise NotImplementedError("This method is not exposed yet")

    @cache
    @staticmethod
    def _get_creds() -> tuple[str, str]:
        # Get default credentials and project ID
        credentials, project_id = cast(tuple[Credentials, str], default())  # type: ignore[no-untyped-call]
        # Refresh credentials to ensure token is valid
        credentials.refresh(Request())  # type: ignore[no-untyped-call]

        # Extract the access token
        token = credentials.token
        if token is None:
            # Token may be None until credentials are refreshed/valid; treat as error in strict mode
            raise RuntimeError("Failed to obtain access token from Google credentials")
        access_token: str = token

        return access_token, project_id

    @staticmethod
    def _run_process(action: str, *args: str) -> None:
        """Run the external blockcachevfsd helper with the specified action and arguments.

        This function retrieves credentials via CloudSqlite._get_creds(), locates the
        blockcachevfsd executable next to this module file, and invokes it using
        subprocess.run(check=True). The command is constructed with the given action,
        Google module settings, and the retrieved project/user and access token.

        Args:
            action: The operation to perform (e.g., "start", "stop", "status").
            *args: Additional command-line arguments passed through to blockcachevfsd.
        """
        access_token, project_id = CloudSqlite._get_creds()
        lib_path = os.path.abspath(__file__)
        subprocess.run(
            [
                os.path.dirname(lib_path) + "/blockcachevfsd",
                action,
                "-module",
                "google",
                "-user",
                project_id,
                "-auth",
                access_token,
                *args,
            ],
            check=True,
        )

    @staticmethod
    def destroy_db(bucket_path: str) -> None:
        """Destroy a database in cloud storage.

        Args:
            bucket_path: The path to the bucket in cloud storage.
        """
        CloudSqlite._run_process(
            "destroy",
            bucket_path,
        )

    @staticmethod
    def download_db(bucket_path: str) -> None:
        """Download database from cloud storage.

        Args:
            bucket_path: The path to the bucket in cloud storage.

        ex: ssb-*-data-produkt-prod/**/db
        """
        CloudSqlite._run_process(
            "download",
            "-container",
            bucket_path,
            "testing",
        )

    @staticmethod
    def create_container(bucket_path: str, block_size: str = "2048k") -> None:
        """Create a container in cloud storage.

        Args:
            bucket_path: The path to the bucket in cloud storage.
            block_size: The block size to use.

        ex: ssb-*-data-produkt-prod/**/db
        """
        CloudSqlite._run_process(
            "create",
            "-blocksize",
            block_size,
            bucket_path,
        )

    @staticmethod
    def create_local_db() -> None:
        """Create a local SQLite database."""
        sqlite3.connect("example.db")

    @staticmethod
    def upload_db(bucket_path: str, local_db: str, db_name: str) -> None:
        """Upload database to cloud storage.

        Args:
            bucket_path: The path to the bucket in cloud storage.
            local_db: The path to the local database file.
            db_name: The name of the database in cloud storage.
        """
        CloudSqlite._run_process(
            "upload",
            "-container",
            bucket_path,
            local_db,
            db_name,
        )

    @staticmethod
    def init_db(db_name: str, bucket_location: str, block_size: str = "2048k") -> None:
        """Initialize a new database and upload to cloud storage.

        Args:
            db_name: The name of the database file.
            bucket_location: The location in cloud storage to upload the database.
            block_size: The block size to use.
        """
        conn = sqlite3.connect(db_name)
        conn.execute(
            """
                CREATE TABLE IF NOT EXISTS _ssb_sqlite_metadata (
                    creator VARCHAR,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )"""
        )
        conn.execute(
            """
                    INSERT INTO _ssb_sqlite_metadata (creator) VALUES (?);
                """,
            (os.environ.get("DAPLA_USER"),),
        )
        conn.commit()
        CloudSqlite.create_container(bucket_location, block_size)
        CloudSqlite.upload_db(bucket_location, db_name, db_name)
        os.remove(db_name)

    @staticmethod
    def list_files_db(bucket_path: str) -> None:
        """List files stored in a CloudSqlite-backed bucket.

        This helper delegates to `CloudSqlite._run_process("list", bucket_path)` to
        enumerate files for the given bucket path. It is primarily intended for
        diagnostic or administrative use.

        Args:
            bucket_path (str): The CloudSqlite bucket path or identifier whose files should be listed.
        """
        CloudSqlite._run_process(
            "list",
            bucket_path,
        )

    @staticmethod
    def list_manifest_db(bucket_path: str) -> None:
        """List the manifest database for a given cloud bucket path.

        This convenience wrapper delegates to CloudSqlite._run_process("manifest", bucket_path),
        which executes the "manifest" process and streams its output.

        Args:
            bucket_path (str): Cloud storage bucket path or URI.
        """
        CloudSqlite._run_process(
            "manifest",
            bucket_path,
        )
