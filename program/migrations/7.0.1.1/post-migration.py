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


def create_level_menus(cr, user, pool, context):
    # Get pools
    level_pool = pool['program.result.level']
    menu_pool = pool['ir.ui.menu']
    values_pool = pool['ir.values']
    act_pool = pool['ir.actions.act_window']
    # Get xml_id with references
    template_menu_id = pool['ir.model.data'].get_object_reference(
        cr, user, 'program', 'menu_program_result_result'
    )[1]
    template_action_id = pool['ir.model.data'].get_object_reference(
        cr, user, 'program', 'action_program_result_list'
    )[1]
    for i in level_pool.search(cr, user, [], context=context):
        vals = level_pool.read(cr, user, i, ['name'], context=context)
        # Clone objects
        act_id = act_pool.copy(cr, user, template_action_id, context=context)
        menu_id = menu_pool.copy(cr, user, template_menu_id, context=context)
        # Set menu entry name
        menu_pool.write(
            cr, user, menu_id,
            {
                'name': vals['name'],
                'sequence': 20,
            },
            context=context
        )
        # Link action in menu
        values_id = pool['ir.values'].search(
            cr, user, [('res_id', '=', menu_id)], context=context
        )
        values_pool.write(
            cr, user, values_id,
            {'value': 'ir.actions.act_window,%d' % act_id},
            context=context
        )
        # Create level with menu ref
        level_pool.write(cr, user, i, {
            'menu_id': menu_id,
        }, context=context)
        level_pool.write(cr, user, i, {
            'menu_title': vals['name'],
        }, context=context)
        # Set domain to be only this level
        act_pool.write(
            cr, user, act_id,
            {'domain': [('result_level_id', '=', i)]},
            context=context
        )


def migrate(cr, version):
    if not version:
        return
    pool = pooler.get_pool(cr.dbname)
    context = pool['res.users'].context_get(cr, SUPERUSER_ID)
    create_level_menus(cr, SUPERUSER_ID, pool, context)
