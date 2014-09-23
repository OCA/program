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
logger.setLevel(logging.DEBUG)

column_renames = {
    'program_result_team_partner': [
        ('organisation_id', 'partner_id'),
        ('type_id', 'legacy_update_1_1_type_id'),
    ],
}


def rename_columns(cr, column_spec):
    for table, renames in column_spec.iteritems():
        for old, new in renames:
            logger.info("table %s, column %s: renaming to %s",
                        table, old, new)
            cr.execute('ALTER TABLE "%s" RENAME "%s" TO "%s"'
                       % (table, old, new,))
            cr.execute('DROP INDEX IF EXISTS "%s_%s_index"'
                       % (table, old))


def migrate(cr, version):
    if not version:
        return
    rename_columns(cr, column_renames)
