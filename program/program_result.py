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

import re

from openerp.osv import fields, orm
from openerp.tools.translate import _


RE_GROUP_FROM = [
    re.compile("\[\('state', '!=', 'draft'\)\]"),
    re.compile("\[\[&quot;state&quot;, &quot;!=&quot;, &quot;draft&quot;\]\]"),
]
RE_GROUP_TO = [
    "[('state', 'not in', ('draft', 'validated'))]",
    "[[&quot;state&quot;, &quot;not in&quot;, "
    "[&quot;draft&quot;, &quot;validated&quot;]]]",
]


class program_result(orm.Model):

    _name = 'program.result'
    _description = 'Result'
    _inherit = ['mail.thread']
    _parent_name = 'parent_id'

    def _get_descendants(self, cr, uid, ids, name=None, args=None,
                         context=None):
        """Return any result which is either a child or recursively a child
        of result.
        """
        res = {}
        if context is None:
            context = {}
        if type(ids) is not list:
            ids = [ids]
        for result in self.browse(cr, uid, ids, context=context):
            child_list = [r.id for r in result.child_ids]
            for child in result.child_ids:
                child_list += child._get_descendants(child.id)[child.id]
            res[result.id] = child_list
        return res

    def _get_parent_id(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        return {
            result.id: result.parent_id.id
            for result in self.browse(cr, uid, ids, context=context)
        }

    def _transverse_label(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        string = _('%s contributes to')
        if ids is None:
            return string % ''
        return {
            result.id: string % result.name or ''
            for result in self.browse(cr, uid, ids, context=context)
        }

    def _transverse_inv_label(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        string = _('Contributed by %s')
        if ids is None:
            return string % ''
        return {
            result.id: string % result.name or ''
            for result in self.browse(cr, uid, ids, context=context)
        }

    def _clear_transversal(self, cr, user, ids, context=None):
        """Transverse all children and remove their transversal relations"""
        for result in self.browse(cr, user, ids, context=context):
            child_ids = [child.id for child in result.child_ids]
            self._clear_transversal(cr, user, child_ids, context=context)
            result.write({
                'transverse_child_ids': [(6, False, [])],
                'transverse_parent_ids': [(6, False, [])],
            })

    def _result_level_id(
            self, cr, user, ids=False, parent_id=False, context=None):
        if parent_id:
            depth = self.read(cr, user, parent_id, ['depth'])['depth'] + 1
        else:
            depth = 1
        level_pool = self.pool['program.result.level']
        root_ids = level_pool.search(
            cr, user, [('depth', '=', depth)], context=context
        )
        if root_ids:
            return root_ids[0]
        else:
            return False

    def onchange_parent_id(self, cr, user, ids, parent_id, context=None):
        return {
            'value': {
                'result_level_id': self._result_level_id(
                    cr, user, parent_id=parent_id, context=context
                ),
            }
        }

    def create(self, cr, user, vals, context=None):
        parent_id = vals.get('parent_id')
        if parent_id or parent_id is False:
            vals['result_level_id'] = self._result_level_id(
                cr, user, parent_id=parent_id, context=context
            )
        return super(program_result, self).create(
            cr, user, vals, context=context)

    def write(self, cr, user, ids, vals, context=None):
        """Clear transversals if tree structure has changed"""
        parent_id = vals.get('parent_id')
        if parent_id or parent_id is False:
            vals['result_level_id'] = self._result_level_id(
                cr, user, parent_id=parent_id, context=context
            )
        res = super(program_result, self).write(
            cr, user, ids, vals, context=context
        )

        if 'parent_id' in vals and not context.get('install_mode'):
            self._clear_transversal(cr, user, ids, context=context)

        return res

    def fields_view_get(
            self, cr, uid, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        """Change the readonly fields depending on the groups

        Look for the strings "[('state', '!=', 'draft')]"
        exactly in the xml view and replace it with
        "[('state', 'not in', ('draft', 'validated'))]"
        """
        user_pool = self.pool['res.users']
        res = super(program_result, self).fields_view_get(
            cr, uid, view_id, view_type, context, toolbar, submenu
        )
        if (user_pool.has_group(cr, uid, 'program.group_program_director')
                and view_type == 'form'):
            for FROM, TO in zip(RE_GROUP_FROM, RE_GROUP_TO):
                res['arch'] = FROM.sub(TO, res['arch'])
        return res

    _columns = {
        'name': fields.char(
            'Name', required=True, select=True, translate=True,
            track_visibility='onchange',
        ),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('validated', 'Validated'),
                ('opened', 'Opened'),
                ('closed', 'Closed'),
                ('cancel', 'Cancelled'),
            ],
            'Status', select=True, required=True, readonly=True,
        ),
        'long_name': fields.char(
            'Long name', translate=True, track_visibility='onchange',
        ),
        'parent_id': fields.many2one(
            'program.result', string='Parent', select=True,
            track_visibility='onchange',
        ),
        'parent_id2': fields.function(
            _get_parent_id, type='many2one', relation='program.result',
            string='Parent', readonly=True),
        'child_ids': fields.one2many(
            'program.result', 'parent_id', string='Child Results',
            track_visibility='onchange',
        ),
        'descendant_ids': fields.function(
            _get_descendants, type='one2many', relation='program.result',
            string='Descendant', readonly=True),
        'transverse_child_ids_label': fields.function(
            _transverse_label, type='char', string='Contributes to Label'),
        'transverse_child_ids': fields.many2many(
            'program.result', 'transverse_rel', 'from_id', 'to_id',
            string='Contributes to', track_visibility='onchange',
        ),
        'transverse_parent_ids_label': fields.function(
            _transverse_inv_label, type='char',
            string='Contributed by label'),
        'transverse_parent_ids': fields.many2many(
            'program.result', 'transverse_rel', 'to_id', 'from_id',
            string='Contributed by', track_visibility='onchange',
        ),
        'code': fields.char('Code', size=32, track_visibility='onchange'),
        'result_level_id': fields.many2one(
            'program.result.level', string='Level', select=True,
            track_visibility='onchange', required=True,
        ),
        'depth': fields.related(
            'result_level_id', 'depth', type="integer", string='Depth',
        ),
        'date_from': fields.date('Start Date', track_visibility='onchange'),
        'date_to': fields.date('End Date', track_visibility='onchange'),
        'description': fields.text('Description', translate=True),
        'target_audience': fields.text('Target Audience', translate=True),
        'target_audience_type_ids': fields.many2many(
            'program.result.target', string='Target Audience Types'
        ),
        'intervention_id': fields.many2one(
            'program.result.intervention', string='Intervention Mode'
        ),
        'tag_ids': fields.many2many('program.result.tag', string='Tags'),
    }
    _defaults = {
        'state': 'draft',
        'transverse_child_ids_label': (
            lambda self, cr, uid, context:
            self._transverse_label(cr, uid, context=context)
        ),
        'transverse_parent_ids_label': (
            lambda self, cr, uid, context:
            self._transverse_inv_label(cr, uid, context=context)
        ),
        'result_level_id': (
            lambda self, cr, uid, context:
            self._result_level_id(cr, uid, context=context)
        ),
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return "\n\n" + _('Error! You can not create recursive Results.')

    _constraints = [
        (orm.Model._check_recursion, _rec_message, ['parent_id']),
    ]
