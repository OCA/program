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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class program_result_level(orm.Model):

    _inherit = 'program.result.level'
    _columns = {
        'top_level_menu': fields.boolean('Has Top Level Menu'),
        'top_level_menu_name': fields.char('Top Level Menu Name'),
        'top_level_menu_id': fields.many2one('ir.ui.menu', 'Top Level Menu'),
    }

    def validate_vals(self, vals):
        top_level_menu = vals.get('top_level_menu')
        if top_level_menu is False:
            vals['top_level_menu_name'] = False
        top_level_menu_name = vals.get('top_level_menu_name')
        parent_id = vals.get('parent_id')

        if top_level_menu and not top_level_menu_name:
            raise orm.except_orm(
                _('Error!'),
                _('No Menu Name provided')
            )

        if parent_id and top_level_menu:
            raise orm.except_orm(
                _('Error!'),
                _('Top level menus can only be set on the highest level '
                  'of a result chain')
            )

    def _get_custom_domain(self, menu_ref, top_level_menu_id):
        if menu_ref == 'program.menu_program_result_chain':
            return [
                ('result_level_id.top_level_menu_id', '=', top_level_menu_id),
            ]
        elif menu_ref == 'program.menu_program_configuration_level':
            return [
                ('chain_root.top_level_menu_id', '=', top_level_menu_id),
            ]
        return [
            ('top_level_menu_id', '=', top_level_menu_id),
        ]

    def _get_custom_context(self, menu_ref, top_level_menu_id):
        if menu_ref in ['program.menu_program_result_chain',
                        'program.menu_program_configuration_level']:
            return {}
        return {'default_top_level_menu_id': top_level_menu_id}

    def create_menus(self, cr, user, vals, context=None):
        model_data_pool = self.pool['ir.model.data']

        top_level_menu_id = self.pool['ir.ui.menu'].create(
            cr, user, {
                'name': vals['top_level_menu_name'],
                'sequence': model_data_pool.get_object(
                    cr, user, 'program', 'menu_program'
                ).sequence,
            }, context=context
        )
        vals['top_level_menu_id'] = top_level_menu_id
        parent_id = self._clone_ref(
            cr, user,
            'program.menu_program_result',
            {'parent_id': top_level_menu_id},
            context=context
        )
        self._clone_menu_action(
            cr, user,
            'program.menu_program_result_chain',
            'program.action_program_result_tree',
            menu_default={'parent_id': parent_id},
            additional_domain=self._get_custom_domain(
                'program.menu_program_result_chain', top_level_menu_id
            ), context=context
        )

        # Configuration
        menu_configuration_id = self._clone_ref(
            cr, user,
            'program.menu_program_configuration',
            {'parent_id': top_level_menu_id},
            context=context
        )
        for child_id in model_data_pool.get_object(
            cr, user, 'program', 'menu_program_configuration'
        ).child_id:
            menu_ref = child_id.get_external_id()[child_id.id]
            action_ref = child_id.action.get_external_id()[child_id.action.id]
            self._clone_menu_action(
                cr, user, menu_ref, action_ref,
                menu_default={'parent_id': menu_configuration_id},
                additional_domain=self._get_custom_domain(
                    menu_ref, top_level_menu_id
                ),
                additional_context=self._get_custom_context(
                    menu_ref, top_level_menu_id
                ), context=context
            )

        return parent_id

    def create(self, cr, user, vals, context=None):
        self.validate_vals(vals)
        parent_id = False

        if vals.get('top_level_menu'):
            parent_id = self.create_menus(cr, user, vals, context=context)

        res = super(program_result_level, self).create(
            cr, user, vals, context=context
        )

        self.post_write_menu_writes(cr, user, res, parent_id, vals,
                                    context=context)

        return res

    def write(self, cr, user, ids, vals, context=None):
        """Bubble up Top Menu configuration if chain root changes"""
        if isinstance(ids, (int, long)):
            ids = [ids]

        self.validate_vals(vals)
        top_level_menu = vals.get('top_level_menu')

        for level in self.browse(cr, user, ids, context=context):
            if (vals.get('parent_id') is not False
                    and level.depth > 1
                    and top_level_menu):
                raise orm.except_orm(
                    _('Error!'),
                    _('Top level menus can only be set on the highest level '
                      'of a result chain')
                )

        parent_id = False

        if vals.get('top_level_menu'):
            parent_id = self.create_menus(cr, user, vals, context=context)

        res = super(program_result_level, self).write(
            cr, user, ids, vals, context=context
        )

        if 'parent_id' in vals:
            self._bubble_up_menu(cr, user, ids, context=context)

        self.post_write_menu_writes(cr, user, ids, parent_id,
                                    vals, context=context)

        return res

    def post_write_menu_writes(self, cr, user, ids, parent_id,
                               vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]

        for level in self.browse(cr, user, ids, context=context):
            if level.parent_id and level.chain_root.top_level_menu:
                # Get the first submenu
                parent_id = level.chain_root.top_level_menu_id.child_id[0].id

            if parent_id or vals.get('top_level_menu'):
                level.menu_id.write({'parent_id': parent_id})

    def _bubble_up_menu(self, cr, user, ids, context=None):
        """Bubble up Top Menu configuration to root of chain"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        for level in self.browse(cr, user, ids, context=context):
            if not level.parent_id or not level.top_level_menu:
                continue
            top_level_menu = level.top_level_menu
            top_level_menu_name = level.top_level_menu_name
            top_level_menu_id = level.top_level_menu_id.id
            level.write({
                'top_level_menu': False,
                'top_level_menu_name': False,
                'top_level_menu_id': False,
            })
            root = level.chain_root
            if not root.top_level_menu:
                root.write({
                    'top_level_menu': top_level_menu,
                    'top_level_menu_name': top_level_menu_name,
                    'top_level_menu_id': top_level_menu_id,
                })
