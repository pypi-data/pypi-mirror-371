#
#    Copyright (C) 2023 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging


from .s3_api.odoo_s3_fs import S3Odoo

try:
    import odoo
    from odoo import release
    from odoo.modules import module

    odoo_version = release.version_info[0]
except ImportError:
    odoo_version = 0

_logger = logging.getLogger(__name__)


def can_be_activate(for_version: int = None):
    for_version = for_version or odoo_version
    if for_version < 11:
        _logger.warning("Not loaded : Odoo version [%s] not supported", for_version)
        return False
    try:
        s3 = S3Odoo.connect_from_env()
    except AssertionError:
        _logger.info("Not loaded : No bucket !")
        return False
    if not s3 or not s3.conn.enable or not s3.conn.s3_session:
        _logger.warning("Not loaded : S3 connection is not enabled")
        return False
    s3.create_bucket_if_not_exist()
    return True


def _post_load_module():
    if "odoo_filestore_s3" not in odoo.conf.server_wide_modules or not can_be_activate():
        _logger.info("No module in server wide modules")
        return False
    from . import wrapt_patcher  # noqa
