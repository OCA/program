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

from openerp import SUPERUSER_ID

import logging

logger = logging.getLogger('upgrade')
logger.setLevel(logging.DEBUG)


def m2o_to_x2m(cr, model, table, field, source_field):
    """
    Transform many2one relations into one2many or many2many.
    Use rename_columns in your pre-migrate
    script to retain the column's old value, then call m2o_to_x2m
    in your post-migrate script.

    :param model: The target model registry object
    :param table: The source table
    :param field: The new field name on the target model
    :param source_field: the (renamed) many2one column on the source table.

    .. versionadded:: 7.0
    """
    cr.execute('SELECT id, %(field)s '
               'FROM %(table)s '
               'WHERE %(field)s is not null' % {
                   'table': table,
                   'field': source_field,
               })
    for row in cr.fetchall():
        model.write(cr, SUPERUSER_ID, row[0], {field: [(4, row[1])]})


def migrate(cr, version):
    if not version:
        return
    m2o_to_x2m(
        cr,
        'program.result.team.partner',
        'program_result_team_partner',
        'type_id',
        'legacy_update_1_1_type_id'
    )
