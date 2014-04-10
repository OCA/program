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


class program_result(orm.Model):

    _name = 'program.result'
    _parent_name = 'parent_result'

    def _parent_result_search(self, cr, uid, obj, name, args, context=None):

        try:
            action_id = context['action']
        except KeyError:
            raise orm.except_orm(
                _('Error!'), _('Action is absent from context.'))

        action_pool = self.pool.get('program.action')
        action = action_pool.browse(cr, uid, action_id, context=context)

        results = []
        parent = action.parent

        while parent:
            if not parent.results and parent.parent_result:
                results = [parent.parent_result.id]
                break
            elif parent.results:
                results = [r.id for r in parent.results]
                break
            parent = parent.parent

        return [('id', 'in', results)]

    def _planned_children(self, cr, uid, ids, name, arg, context=None):
        # TODO

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        for result in self.browse(cr, uid, ids, context=context):
            res[result.id] = []

        return res

    def name_get(self, cr, uid, ids, context=None):
        res = []

        if not isinstance(ids, list):
            ids = [ids]

        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id, ''.join([
                line.result_level and line.result_level.code and
                line.result_level.code + ' - ' or '',
                (line.code and line.code + ' - ') or '',
                line.name]))
            )

        return res

    def _get_level_code(self, cr, uid, ids, field_name, args, context=None):
        if not isinstance(ids, list):
            ids = [ids]

        return {
            line.id: line.result_level.code or line.result_level.name
            for line in self.browse(cr, uid, ids, context=context)
        }

    def _get_child_results(self, cr, uid, ids, field, args=[], context=None):
        if not isinstance(ids, list):
            ids = [ids]
        return {
            result.id: self.search(
                cr, uid,
                [('parent_action', 'in',
                  [a.id for a in result.child_actions])],
                context=context)
            for result in self.browse(cr, uid, ids, context=context)
        }

    _columns = {
        'name': fields.char('Name', size=128, required=True, select=True),
        'code': fields.char('Code', size=32),
        'result_level': fields.many2one(
            'program.result.level', string='Level', required=True,
            select=True),
        'parent_action': fields.many2one(
            'program.action', string='Parent Action', select=True),
        'child_actions': fields.one2many(
            'program.action', 'parent_result', string='Child Actions'),
        'parent_result': fields.related(
            'parent_action', 'parent_result', type='many2one', store=True,
            relation='program.result', string='Parent Result'),
        'children_result': fields.function(
            _get_child_results, type='one2many', relation='program.result',
            method=True),
        'parent_result_search': fields.function(
            lambda **x: True, fnct_search=_parent_result_search,
            type='boolean', method=True),
        'description': fields.text('Description'),
        'expected_child_results': fields.text('Expected Child Results'),
        'planned_children': fields.function(
            _planned_children, type='one2many', obj='program.action',
            method=True, string='Planned Children'),
        'level_code': fields.function(
            _get_level_code, type='char', method=True, string="Level")
    }
