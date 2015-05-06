# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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

from openerp.osv import orm


class program_result_level(orm.Model):

    _inherit = 'program.result.level'

    def create_menus(self, cr, user, vals, context=None):
        model_data_pool = self.pool['ir.model.data']
        parent_id, old_to_new = super(program_result_level, self).create_menus(
            cr, user, vals, context=context
        )
        top_level_menu_id = vals['top_level_menu_id']

        # Clone Evaluation Menu
        menu_program = model_data_pool.get_object(
            cr, user, 'program', 'menu_program_configuration'
        )
        old_to_new[menu_program.id] = menu_evaluation_id = self._clone_ref(
            cr, user,
            'program_evaluation.menu_program_evaluation_action',
            {'parent_id': top_level_menu_id},
            copy_name=True,
            context=context
        )
        for child_id in model_data_pool.get_object(
            cr, user, 'program_evaluation', 'menu_program_evaluation_action'
        ).child_id:
            menu_ref = child_id.get_external_id()[child_id.id]
            action_ref = child_id.action.get_external_id()[child_id.action.id]
            old_to_new[child_id.id] = self._clone_menu_action(
                cr, user, menu_ref, action_ref,
                menu_default={'parent_id': menu_evaluation_id},
                additional_domain=self._get_custom_domain(
                    menu_ref, top_level_menu_id
                ),
                additional_context=self._get_custom_context(
                    menu_ref, top_level_menu_id
                ),
                copy_name=True,
                context=context
            )[0]

        return parent_id, old_to_new
