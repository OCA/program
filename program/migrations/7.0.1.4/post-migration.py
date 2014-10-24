# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) 2010 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import pooler, SUPERUSER_ID

import logging

logger = logging.getLogger('upgrade')
logger.setLevel(logging.DEBUG)


def get_legacy_name(original_name):
    return 'upgrade_legacy_1_4_%s' % original_name


def merge_execution(cr, uid, pool, context):
    def merge_fields(pool_obj, source, target):
        legacy_name = get_legacy_name(source)
        cr.execute("""\
SELECT id, %s
FROM %s
""" % (legacy_name, pool_obj._table))
        for obj_id, field in cr.fetchall():
            if not field:
                continue
            pool_obj.write(cr, uid, obj_id, {
                target: field,
            }, context=context)
    merge_fields(pool['program.result'], 'execution', 'status')
    merge_fields(
        pool['program.result.level'],
        'fvg_show_field_execution',
        'fvg_show_group_status',
    )
    merge_fields(
        pool['program.result.level'],
        'fvg_show_field_status',
        'fvg_show_group_status',
    )


def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    context = pool['res.users'].context_get(cr, SUPERUSER_ID)
    merge_execution(cr, SUPERUSER_ID, pool, context)
