from __future__ import annotations

from odoo_env_config.api import EnvOdooConfig, SimpleKey


class FilestoreS3EnvConverter(EnvOdooConfig):
    _ini_section = "odoo_s3_filestore"

    access_key: str = SimpleKey("S3_FILESTORE_ACCESS_KEY", ini_dest="s3_access_key")
    secret: str = SimpleKey("S3_FILESTORE_SECRET_KEY", ini_dest="s3_secret")
    region: str = SimpleKey("S3_FILESTORE_REGION", init_dest="s3_region")
    host: str = SimpleKey("S3_FILESTORE_HOST", init_dest="s3_host")
    bucket_name: str = SimpleKey("S3_FILESTORE_BUCKET", ini_dest="s3_bucket_name")
    secure: bool = SimpleKey("S3_SECURE", py_default=True, ini_dest="s3_secure")
    sub_dir: bool = SimpleKey("S3_FILESTORE_SUB_DIR", ini_dest="sub_dir_by_dbname")
