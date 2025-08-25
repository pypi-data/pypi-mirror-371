"""
Contains the mapper specifique for the environment variable provided by CleverCloud addons.
Currently we support :
- S3 addons Cellar
- Postgres Addons of any scaler
"""

from odoo_env_config.api import Env


def s3_clevercloud_cellar(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "CELLAR_ADDON_HOST"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "CELLAR_ADDON_KEY_SECRET"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEY", "CELLAR_ADDON_KEY_ID"),
        "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "ODOO_S3_BUCKET"),
        # S3 CleverCloud don't provide region
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "CELLAR_ADDON_REGION", "ODOO_S3_REGION"),
    }


def s3_minio(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "MINIO_DOMAIN"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "MINIO_SECRET_KEY"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEY", "MINIO_ACCESS_KEY"),
        "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "MINIO_BUCKET"),
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "MINIO_REGION"),
        "S3_SECURE": curr_env.gets("S3_FILESTORE_SECURE", "MINIO_SECURE"),
    }


def s3filestore_compat(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "ODOO_S3_HOST"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "ODOO_S3_SECRET_KEY"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEYODOO_S3_ACCESS_KEY"),
        "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "ODOO_S3_BUCKET"),
        # Pas de region fournit par S3 CleverCloud
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "ODOO_S3_REGION"),
        "S3_SECURE": curr_env.gets("S3_FILESTORE_SECURE", "ODOO_S3_SECURE"),
    }
