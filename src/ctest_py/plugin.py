import sqlite3
import os
from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
import subprocess

import ctypes
from functools import cache

class CloudSqlite:
    def __init__(self, bucket: str, vfs_name = "ssb_vfs", cache_dir = "./cache", bucket_alias = "buckets") -> None:
        """
        Loads the extension into sqlite.
        Can connect to the database like this:
        >>> import sqlite3
        >>> sqlite3.connect(f"file:/{bucket_alias}/{database_name}?vfs={vfs_name}", uri=True)
        
        Args:
            bucket (str): Bucket path. ex: ssb-vare-tjen-korttid-data-produkt-prod/vhi/db
            vfs_name (str): The vfs name used to access the extension
            cache_dir (str): The path to the directory used for caching. Will create the directory if it does not exists
            bucket_alias (str): The alias for the bucket.
        
        Returns:
            None
        
        Raises:
            sqlite3.OperationalError: If the exstension cannot be loaded.
        """
        access_token, project_id = CloudSqlite._get_creds()

        if os.path.exists(cache_dir) == False:
            os.makedirs(cache_dir, exist_ok=True)

        os.environ["CS_KEY"] = access_token
        os.environ["CS_ACCOUNT"] = project_id
        os.environ["SQ_VFS_NAME"] = vfs_name
        os.environ["SQ_CACHE_DIR"] = cache_dir
        os.environ["SQ_DB_BUCKET"] = bucket
        os.environ["SQ_CONTAINER_ALIAS"] = bucket_alias
        os.environ["SQ_VERBOSITY"] = "0"

        lib_path = os.path.abspath(__file__)
        EXTENSION_PATH = os.path.dirname(lib_path) + "/exstension"
        # Step 1: Load the extension using a temporary connection
        temp_conn = sqlite3.connect(":memory:")
        temp_conn.enable_load_extension(True)

        try:
            # The extension's entry point should register the 'myvfs' VFS persistently.
            temp_conn.load_extension(EXTENSION_PATH)
            print(f"Extension loaded successfully from {EXTENSION_PATH}")
        except sqlite3.OperationalError as e:
            print(f"Failed to load extension: {e}")
            temp_conn.close()
            exit()

        temp_conn.close()

    @staticmethod
    def clean_blocks():
        # TODO fix this function. Unknown memory error
        raise NotImplementedError("This method needs more testing")
            
        print("cleaning")
        lib_path = os.path.abspath(__file__)
        lib = ctypes.CDLL( os.path.dirname(lib_path) + "/exstension.so")
        lib.clean.argtypes = []
        lib.clean.restype = ctypes.c_void_p
        lib.clean()

    @cache
    @staticmethod
    def _get_creds():
        # Get default credentials and project ID
        credentials, project_id = default()  # pyright: ignore
        credentials: Credentials
        project_id: str
        # Refresh credentials to ensure token is valid
        credentials.refresh(Request())

        # Extract the access token
        access_token: str = credentials.token  # pyright: ignore

        return access_token, project_id

    @staticmethod
    def _run_process(action, *args):
        access_token, project_id = CloudSqlite._get_creds()
        lib_path = os.path.abspath(__file__)
        p = subprocess.run(
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
            check=True
        )

    @staticmethod
    def destroy_db(bucket_path: str):
        CloudSqlite._run_process(
            "destroy",
            bucket_path,
        )

    @staticmethod
    def download_db(bucket_path: str):
        """ex: ssb-*-data-produkt-prod/**/db"""
        CloudSqlite._run_process(
            "download",
            "-container",
            bucket_path,
            "testing",
        )

    @staticmethod
    def create_container(bucket_path: str, block_size="2048k"):
        """ex: ssb-*-data-produkt-prod/**/db"""
        CloudSqlite._run_process(
            "create",
            "-blocksize",
            block_size,
            bucket_path,
        )

    @staticmethod
    def create_local_db():
        sqlite3.connect("example.db")

    @staticmethod
    def upload_db(bucket_path: str, local_db: str, db_name: str):
        CloudSqlite._run_process(
            "upload",
            "-container",
            bucket_path,
            local_db,
            db_name,
        )
    @staticmethod
    def init_db(db_name: str, bucket_location: str, block_size="2048k"):
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
    def list_files_db(bucket_path: str):
        CloudSqlite._run_process(
            "list",
            bucket_path,
        )

    @staticmethod
    def list_manifest_db(bucket_path: str):
        CloudSqlite._run_process(
            "manifest",
            bucket_path,
        )

