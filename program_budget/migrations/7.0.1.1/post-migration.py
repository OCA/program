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


def logged_query(cr, query, args=None):
    """
    Logs query and affected rows at level DEBUG
    """
    if args is None:
        args = []
    cr.execute(query, args)
    logger.debug('Running %s', query % tuple(args))
    logger.debug('%s rows affected', cr.rowcount)
    return cr.rowcount


def restore_countries(cr, uid, pool, context):
    """Create the new object program.result.country from backed-up
     country ids
     """
    country_pool = pool['program.result.country']
    logged_query(cr, """
ALTER TABLE program_result_program_result_country_rel
ADD COLUMN program_result_country_id integer
""")
    cr.execute("""
SELECT DISTINCT program_result_id, res_country_id_legacy_7_0_1_1
FROM program_result_program_result_country_rel
""")
    for result_id, country_id in cr.fetchall():
        new_id = country_pool.create(
            cr, uid, {'name': country_id, 'result_id': result_id},
            context=context
        )
        logged_query(cr, """
UPDATE program_result_program_result_country_rel
SET program_result_country_id = %s
WHERE res_country_id_legacy_7_0_1_1 = %s
""", (new_id, country_id))
    logged_query(cr, """
ALTER TABLE program_result_program_result_country_rel
ALTER COLUMN program_result_country_id SET NOT NULL
""")
    logged_query(cr, """
ALTER TABLE program_result_program_result_country_rel
ALTER COLUMN res_country_id_legacy_7_0_1_1 DROP NOT NULL
""")


def m2m_to_o2m(cr, uid, pool, model, field, m2m_table, id1, id2, context):
    pool1 = pool[model]
    pool2 = pool[pool1._columns[field]._obj]
    cr.execute("""
SELECT %s, %s
FROM %s
""" % (id1, id2, m2m_table))
    used_ids = []
    for f1, f2 in cr.fetchall():
        if f2 in used_ids:
            f2 = pool2.copy(cr, uid, f2, {'result_id': f1}, context=context)
        used_ids.append(f2)
        pool1.write(cr, uid, f1, {field: [(4, f2)]}, context=context)


def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    context = pool['res.users'].context_get(cr, SUPERUSER_ID)
    restore_countries(cr, SUPERUSER_ID, pool, context)
    m2m_to_o2m(
        cr,
        SUPERUSER_ID,
        pool,
        'program.result',
        'target_country_ids',
        'program_result_program_result_country_rel',
        'program_result_id',
        'program_result_country_id',
        context,
    )
