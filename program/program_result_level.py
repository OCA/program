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

"""Configuration of a level of result

Boolean fields which start in fvg_show_page_ or fvg_show_field_ or
any fvg_show_<type>_<name> will result in a configuration option to
show or hide a certain element of <type> and <name> in the form view
of a result.
"""

from openerp.osv import fields, orm
from openerp.tools.translate import _


class program_result_level(orm.Model):

    _name = 'program.result.level'
    _description = 'Result Level'
    _parent_name = 'parent_id'

    def create(self, cr, user, vals, context=None):
        """Create a menu entry for each level

        Clone regular result view
        Clone regular result view action
        Redirect link through ir.values so new view links to new action
        """
        # Get pools
        trans_pool = self.pool['ir.translation']
        menu_pool = self.pool['ir.ui.menu']
        values_pool = self.pool['ir.values']
        act_pool = self.pool['ir.actions.act_window']
        # Get xml_id with references
        template_menu_id = self.pool['ir.model.data'].get_object_reference(
            cr, user, 'program', 'menu_program_result_result'
        )[1]
        template_action_id = self.pool['ir.model.data'].get_object_reference(
            cr, user, 'program', 'action_program_result_list'
        )[1]
        # Clone objects
        act_id = act_pool.copy(cr, user, template_action_id, context=context)
        menu_id = menu_pool.copy(cr, user, template_menu_id, context=context)
        # Fix duplication of translation
        trans_ids = trans_pool.search(
            cr, user, [('res_id', 'in', [act_id, menu_id])], context=context
        )
        trans_pool.unlink(cr, user, trans_ids, context=context)
        # Set menu entry name
        menu_pool.write(
            cr, user, menu_id,
            {'name': vals['name']},
            context=context
        )
        # Link action in menu
        values_id = self.pool['ir.values'].search(
            cr, user, [('res_id', '=', menu_id)], context=context
        )
        values_pool.write(
            cr, user, values_id,
            {'value': 'ir.actions.act_window,%d' % act_id},
            context=context
        )
        # Create level with menu ref
        vals['menu_id'] = menu_id
        res = super(program_result_level, self).create(
            cr, user, vals, context=context
        )
        # Set domain to be only this level
        act_vals = {'domain': [('result_level_id', '=', res)]}
        parent_id = vals.get('parent_id')
        if parent_id:
            depth = self.read(
                cr, user, parent_id, ['depth'], context=context
            )['depth']
            act_vals['context'] = {'default_parent_depth': depth}
        else:
            act_vals['context'] = {'default_parent_depth': -1}
        act_pool.write(cr, user, act_id, act_vals, context=context)
        return res

    def write(self, cr, user, ids, vals, context=None):
        """Update menu entry for each level"""
        name = vals.get('name')
        parent_id = vals.get('parent_id')

        for level in self.browse(cr, user, ids, context=context):
            if name:
                level.menu_id.write({'name': name})
            if parent_id is not None:
                depth = self.read(
                    cr, user, parent_id, ['depth'], context=context
                )['depth']
                if parent_id is False:
                    level.menu_id.action({'context': False})
                else:
                    level.menu_id.action.write({
                        'context': {'default_parent_depth': depth}
                    })
        return super(program_result_level, self).write(
            cr, user, ids, vals, context=context
        )

    def unlink(self, cr, uid, ids, context=None):
        menu_pool = self.pool['ir.ui.menu']
        menu_ids = set(
            l['menu_id'][0]
            for l in self.read(cr, uid, ids, ['menu_id'], context=context)
        )
        res = super(program_result_level, self).unlink(
            cr, uid, ids, context=context
        )
        res &= menu_pool.unlink(cr, uid, list(menu_ids), context=context)
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        return [(line.id, (line.code and line.code + ' - ' or '') + line.name)
                for line in self.browse(cr, uid, ids, context=context)]

    def _get_depth(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        if type(ids) is not list:
            ids = [ids]
        return {
            level.id: (
                self._get_depth(
                    cr, uid, level.parent_id.id, context=context
                )[level.parent_id.id] if level.parent_id else 0) + 1
            for level in self.browse(cr, uid, ids, context=context)
        }

    _columns = {
        'name': fields.char(
            'Name', size=128, required=True, select=True, translate=True),
        'result_ids': fields.one2many(
            'program.result', 'result_level_id', string='Result'),
        'code': fields.char('Code', size=32, translate=True),
        'parent_id': fields.many2one('program.result.level', 'Parent'),
        'child_id': fields.one2many(
            'program.result.level', fields_id='parent_id', string='Child',
            limit=1
        ),
        'depth': fields.function(
            _get_depth, type='integer', string='Level', store=True
        ),
        'menu_id': fields.many2one('ir.ui.menu', 'Menu', required=True),
        'fvg_show_page_target': fields.boolean('Show "Targets" Tab'),
        'fvg_show_field_statement': fields.boolean(
            'Show "Statement of Result" Field',
        ),
    }
    _defaults = {
        'fvg_show_page_target': True,
        'fvg_show_field_statement': True,
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return _('Error! You can not create recursive Levels.')

    _constraints = [
        (orm.Model._check_recursion, _rec_message, ['parent_id']),
    ]
