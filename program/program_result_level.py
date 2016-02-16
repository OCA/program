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
from openerp.tools.safe_eval import safe_eval

from .program_result import STATES


class program_result_level(orm.Model):

    _name = 'program.result.level'
    _description = 'Result Level'
    _parent_name = 'parent_id'

    def _clone_ref(self, cr, user, ref, defaults=None, copy_name=False,
                   context=None):
        """Given a ref, copy it, write defaults and return the new id"""
        model_data_pool = self.pool['ir.model.data']
        module, res_name = ref.split('.')
        model, res_id = model_data_pool.get_object_reference(
            cr, user, module, res_name
        )
        ref_model = self.pool[model]
        new_id = ref_model.copy(cr, user, res_id, context=context)
        if copy_name and not defaults.get('name'):
            defaults['name'] = ref_model.read(
                cr, user, res_id, ['name'], context=context
            )['name']
        if defaults:
            ref_model.write(cr, user, new_id, defaults, context=context)
        return new_id

    def _clone_menu_action(self, cr, user,
                           menu_ref, action_ref,
                           menu_default=None, action_default=None,
                           additional_domain=None,
                           additional_context=None,
                           copy_name=False,
                           context=None):
        """Clone the pair of menu and action, then link them,
        add elements to the domain
        """
        # Clone
        new_menu_id = self._clone_ref(
            cr, user, menu_ref, menu_default, copy_name=copy_name,
            context=context
        )
        new_action_id = self._clone_ref(
            cr, user, action_ref, action_default, context=context
        )
        # Link
        values_pool = self.pool['ir.values']
        values_id = self.pool['ir.values'].search(
            cr, user, [('res_id', '=', new_menu_id)], context=context
        )
        values_pool.write(
            cr, user, values_id,
            {'value': 'ir.actions.act_window,%d' % new_action_id},
            context=context
        )
        # Tweak domain and context
        if additional_domain or additional_context:
            action_pool = self.pool['ir.actions.act_window']
            data = action_pool.read(
                cr, user, new_action_id, ['domain', 'context'], context=context
            )
            domain = safe_eval(data['domain'] or "[]")
            overwritten_domain_fields = [
                i[0] for i in additional_domain if len(i) == 3
            ]
            domain = [
                i for i in domain
                if not (len(i) == 3 and i[0] in overwritten_domain_fields)
            ]
            domain += additional_domain or []
            act_context = safe_eval(data['context'] or "{}")
            act_context.update(additional_context or {})
            action_pool.write(
                cr, user, new_action_id, {
                    'domain': domain,
                    'context': act_context,
                }, context=context
            )
        if not copy_name:
            # Fix duplication of translation
            trans_pool = self.pool['ir.translation']
            trans_ids = trans_pool.search(
                cr, user,
                [
                    '|',
                    '&',
                    ('name', '=', 'ir.ui.menu,name'),
                    ('res_id', '=', new_menu_id),
                    '&',
                    ('name', '=', 'ir.actions.act_window,name'),
                    ('res_id', '=', new_action_id),
                ],
                context=context
            )
            trans_pool.unlink(cr, user, trans_ids, context=context)
        return new_menu_id, new_action_id

    def _get_basic_user_id(self, cr, user, vals, context=None):
        return self.pool['ir.model.data'].get_object_reference(
            cr, user, 'program', 'group_program_basic_user'
        )[1]

    def _bubble_up_specs(self, cr, user, ids, context=None):
        """Bubble up Specs to root of chain"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        spec_pool = self.pool['program.result.validation.spec']
        for level in self.browse(cr, user, ids, context=context):
            if not level.parent_id or not level.validation_spec_ids:
                continue
            new_level_id = level.chain_root.id
            for spec in level.validation_spec_ids:
                if not spec_pool.search(
                        cr, user, [
                            ('level_id', '=', new_level_id),
                            ('group_id', '=', spec.group_id.id),
                        ], context=context):
                    spec_pool.write(cr, user, spec.id, {
                        'level_id': new_level_id,
                    }, context=context)
                else:
                    # Duplicate key, remove it
                    spec_pool.unlink(cr, user, [spec.id], context=context)

    def create(self, cr, user, vals, context=None):
        """Create a menu entry for each level

        Clone regular result view
        Clone regular result view action
        Redirect link through ir.values so new view links to new action
        """
        # Get pools
        act_pool = self.pool['ir.actions.act_window']

        if not vals.get('menu_title'):
            vals['menu_title'] = vals['name']

        if not vals.get('status_label'):
            vals['status_label'] = _("Status of the %s") % vals['name']

        # Clone objects and set menu entry name
        menu_id, act_id = self._clone_menu_action(
            cr, user,
            'program.menu_program_result_result',
            'program.action_program_result_list',
            menu_default={
                'name': vals['menu_title'],
                'groups_id': [(6, 0, [
                    self._get_basic_user_id(cr, user, vals, context)
                ])],
                'sequence': 20,
            },
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
        act_vals['context'].update({'default_result_level_id': res})
        act_vals['name'] = vals['menu_title']
        act_pool.write(cr, user, act_id, act_vals, context=context)
        return res

    def write(self, cr, user, ids, vals, context=None):
        """Update menu entry for each level"""
        if isinstance(ids, (int, long)):
            ids = [ids]
        menu_title = vals.get('menu_title')
        parent_id = vals.get('parent_id')

        for level in self.browse(cr, user, ids, context=context):
            if menu_title:
                level.menu_id.write({'name': menu_title})
                level.menu_id.action.write({'name': vals['menu_title']})
            if parent_id is not None:
                if parent_id is False:
                    level.menu_id.action.write({'context': {}})
                else:
                    depth = self.read(
                        cr, user, parent_id, ['depth'], context=context
                    )['depth']
                    level.menu_id.action.write({
                        'context': {'default_parent_depth': depth}
                    })
        res = super(program_result_level, self).write(
            cr, user, ids, vals, context=context
        )

        if 'parent_id' in vals:
            self._bubble_up_specs(cr, user, ids, context=context)

        return res

    def unlink(self, cr, uid, ids, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
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

    def onchange_name(self, cr, uid, ids, name, context=None):
        res = {}
        if not ids:
            res['value'] = {'menu_title': name}
            res['value'] = {'status_label': _("Status of the %s") % name}
        return res

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

    def _search_chain_end(
            self, cr, uid, model, name=None, args=None, context=None):
        def search_root(level):
            return self.search(
                cr, uid, [('id', 'child_of', level.id)], context=context
            )

        def search_tail(level):
            return search_root(level.chain_root)

        find_chain_ids = search_root if name == 'chain_root' else search_tail
        op = args[0][1]
        ids = args[0][2]
        if isinstance(ids, basestring):
            ids = self.search(cr, uid, [('name', op, ids)], context=context)
        elif isinstance(ids, (int, long)):
            ids = [ids]
        if op in ['=', 'ilike']:
            op = 'in'
        elif op in ['!=', 'not ilike']:
            op = 'not in'
        level_ids = []
        for level in self.browse(cr, uid, ids, context=context):
            if getattr(level, name).id == level.id:
                level_ids += find_chain_ids(level)
        return [('id', op, level_ids)]

    def _get_chain_end(
            self, cr, uid, ids=None, name=None, args=None, context=None):

        def find_root(level):
            return level.parent_id and find_root(level.parent_id) or level

        def find_tail(level):
            return level.child_id and find_tail(level.child_id[0]) or level

        if isinstance(ids, (int, long)):
            ids = [ids]

        find_end_id = find_root if args.get('find_root', True) else find_tail

        return {
            level.id: find_end_id(level).id
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
        'menu_title': fields.char('Menu Title', required=True),
        'fvg_show_page_children': fields.boolean('Show "Results" Tab'),
        'fvg_show_page_risk': fields.boolean(
            'Show "Assumptions and Risks" Tab'
        ),
        'fvg_show_page_target': fields.boolean('Show "Targets" Tab'),
        'fvg_show_group_transversals': fields.boolean(
            'Show Transversal fields',
        ),
        'fvg_show_field_statement': fields.boolean(
            'Show "Title" Field',
        ),
        'fvg_show_group_status': fields.boolean(
            'Show Status of Result Fields',
        ),
        'status_label': fields.char(
            'Label for Status',
            translate=True,
            help='Label to the Status Field.',
        ),
        'status_options': fields.char(
            'Options for Status',
            translate=True,
            help='Comma-separated list of options for the Status Field.',
        ),
        'validation_spec_ids': fields.one2many(
            'program.result.validation.spec',
            'level_id',
            string='Validation Specifications',
            help='Configuration of which users can validate which states',
        ),
        'chain_root': fields.function(
            lambda self, *a, **kw: self._get_chain_end(*a, **kw),
            fnct_search=lambda self, *a, **kw: self._search_chain_end(
                *a, **kw
            ),
            arg={'find_root': True},
            type='many2one',
            relation='program.result.level',
            string='Chain Root',
        ),
        'chain_tail': fields.function(
            lambda self, *a, **kw: self._get_chain_end(*a, **kw),
            fnct_search=lambda self, *a, **kw: self._search_chain_end(
                *a, **kw
            ),
            arg={'find_root': False},
            type='many2one',
            relation='program.result.level',
            string='Chain Tail',
        ),
    }
    _defaults = {
        'fvg_show_page_children': True,
        'fvg_show_page_risk': True,
        'fvg_show_page_target': True,
        'fvg_show_group_transversals': True,
        'fvg_show_group_status': False,
        'fvg_show_field_statement': True,
        'validation_spec_ids': (
            lambda self, *a, **kw: self.default_validation_spec_ids(*a, **kw)
        ),
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return _('Error! You can not create recursive Levels.')

    _constraints = [
        (orm.Model._check_recursion, _rec_message, ['parent_id']),
    ]

    def default_validation_spec_ids(self, cr, uid, context=None):
        """Create default validations from validated to closed using groups
        """
        data_pool = self.pool['ir.model.data']

        def ref(xid):
            return data_pool.get_object(cr, uid, xid[0], xid[1]).id

        groups = [
            ('program', 'group_program_director'),  # validated->visa_director
            ('program', 'group_program_dpe'),  # visa_director->visa_dpe
            ('program', 'group_program_administrator'),  # visa_dpe->visa_admin
            ('program', 'group_program_administrator'),  # visa_admin->opened
            ('program', 'group_program_dpe'),  # opened->closed
        ]
        groups = map(ref, groups)
        states = STATES[1:1+len(groups)]

        res = {}
        for group, state in zip(groups, states):
            res[group] = res.get(group, [])
            res[group].append(state[0])
        return [
            (0, 0, {'group_id': group, 'states': ','.join(res[group])})
            for group in sorted(set(groups))
        ]
