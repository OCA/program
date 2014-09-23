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

import logging

logger = logging.getLogger('upgrade')

xmlid_removes = [
    'program_budget.view_program_result_form_mc',
]

table_renames = [
    ("program_result_res_country_rel",
     "program_result_program_result_country_rel"),
]

column_renames = {
    'program_result_program_result_country_rel': [
        ('res_country_id', 'res_country_id_legacy_7_0_1_1')
    ],
}


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


def table_exists(cr, table):
    """ Check whether a certain table or view exists """
    cr.execute('SELECT 1 FROM pg_class WHERE relname = %s', (table,))
    return cr.fetchone()


def rename_tables(cr, table_spec):
    """
    Rename tables. Typically called in the pre script.
    This function also renames the id sequence if it exists and if it is
    not modified in the same run.

    :param table_spec: a list of tuples (old table name, new table name).

    """
    # Append id sequences
    to_rename = [x[0] for x in table_spec]
    for old, new in list(table_spec):
        if (table_exists(cr, old + '_id_seq') and
                old + '_id_seq' not in to_rename):
            table_spec.append((old + '_id_seq', new + '_id_seq'))
    for (old, new) in table_spec:
        logger.info("table %s: renaming to %s",
                    old, new)
        cr.execute('ALTER TABLE "%s" RENAME TO "%s"' % (old, new,))


def rename_columns(cr, column_spec):
    for table, renames in column_spec.iteritems():
        for old, new in renames:
            logger.info("table %s, column %s: renaming to %s",
                        table, old, new)
            cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"'
                       % (table, old, new,))
            cr.execute('DROP INDEX IF EXISTS "%s_%s_index"'
                       % (table, old))


def remove_xmlid(cr, xmlids_spec):
    for xml_id in xmlids_spec:
        try:
            module, name = xml_id.split('.')
            cr.execute("""
SELECT res_id
FROM ir_model_data
WHERE module=%s AND name=%s
""", (module, name))
            res_id = cr.fetchone()[0]
            logged_query(cr, """
DELETE FROM ir_ui_view
WHERE id=%s
""", (res_id, ))
            logged_query(cr, """
DELETE FROM ir_model_data
WHERE module=%s AND name=%s
""", (module, name))
        except ValueError:
            logger.error(
                'Cannot delete XMLID %s: need the module '
                'reference to be specified in the IDs' % xml_id)


def migrate(cr, version):
    if not version:
        return
    remove_xmlid(cr, xmlid_removes)
    rename_tables(cr, table_renames)
    rename_columns(cr, column_renames)
