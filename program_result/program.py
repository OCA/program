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
from mako.template import Template


class program_action(orm.Model):

    _inherit = 'program.action'

    def _child_results(self, cr, uid, ids, name, arg, context=None):
        # FIXME Needs to be tweaked as per new diagrams!

        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')

        for action in self.browse(cr, uid, ids, context=context):
            results = [result.id for result in action.results]
            child_result_ids = result_pool.search(cr, uid, [('parent_result', 'in', results)], context=context)

            res[action.id] = child_result_ids

        return res

    def _child_results_list(self, cr, uid, ids, name, arg, context=None):

        template = Template("""<ul style="list-style-type: none;margin-left: -130px;">
% for result in results:
  <li><p style="font-weight: bold;">${result['result']}</p>
  % if result['childs']:
    <ul style="list-style-type: none;">
      % for child in result['childs']:
        <li>${child['result']}</li>
      % endfor
    </ul>
  % else:
    % if result['expected']:
      <div class="oe_form_field oe_form_field_text"><span class="oe_form_text_content">${result['expected']}</span></div>
    % endif
  % endif
  </li>
% endfor
</ul>""")

        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')

        for action in self.browse(cr, uid, ids, context=context):
            results = [result.id for result in action.results]
            vals = []
            for result in result_pool.browse(cr, uid, results, context=context):
                val = {
                    'result': result.name_get()[0][1],
                    'expected': result.expected_child_results,
                    'childs': []
                }
                child_result_ids = result_pool.search(
                    cr, uid, [('parent_result', '=', result.id)], context=context)
                if child_result_ids:
                    if not isinstance(child_result_ids, list):
                        child_result_ids = [child_result_ids]

                    for child_result in result_pool.browse(
                            cr, uid, child_result_ids, context=context):
                        child_val = {
                            'result': child_result.name_get()[0][1],
                            'description': child_result.description,
                            'childs': []
                        }
                        val['childs'].append(child_val)

                vals.append(val)

            res[action.id] = template.render(results=vals)

        return res

    _columns = {
        'results': fields.one2many(
            'program.result',
            'parent_action',
            string='Results',
        ),

        'parent_result': fields.many2one(
            'program.result',
            string='Parent Result',
            select=True,
        ),

        'child_results': fields.function(
            _child_results,
            type='one2many',
            obj='program.result',
            method=True,
            string='Child Results',
        ),

        'child_results_list': fields.function(
            _child_results_list,
            type='html',
            method=True,
            string='Child Results',
        ),

        'parent_expected_child_results': fields.related(
            'parent_result',
            'expected_child_results',
            type='text',
            string='Parent Expected Child Results',
            readonly=True,
        ),
    }


class program_result_level(orm.Model):

    _name = 'program.result.level'

    def create(self, cr, uid, data, context=None):
        if context is None:
            context = {}

        depth = data['depth']

        if depth < 0:
            raise orm.except_orm(
                _('Error!'),
                _('Depth must be greater than or equal to 0.')
            )

        return super(
            program_result_level, self).create(cr, uid, data, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        if 'depth' in vals:
            depth = vals['depth']
            if depth < 0:
                raise orm.except_orm(
                    _('Error!'),
                    _('Depth must be greater than or equal to 0.')
                )

        return super(
            program_result_level, self).write(
            cr, uid, ids, vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []

        if not isinstance(ids, list):
            ids = [ids]

        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id, (line.code and line.code + ' - ') + line.name))

        return res

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
        ),

        'result': fields.one2many(
            'program.result',
            'level',
            string='Result',
        ),

        'code': fields.char(
            'Code',
            size=32,
        ),

        'depth': fields.integer(
            'Level',
            required=True,
        ),
    }

    _defaults = {
        'depth': 1,
    }


class program_result(orm.Model):

    _name = 'program.result'
    _parent_name = 'parent_result'

    def _parent_result_search(self, cr, uid, obj, name, args, context=None):
        if context is None:
            context = {}

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
        if context is None:
            context = {}

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
            res.append(
                (line.id,
                 ''.join([
                     line.level and line.level.code  and line.level.code + ' - ' or '',
                     (line.code and line.code + ' - ') or '',
                     line.name]))
            )

        return res

    def _get_level_code(self, cr, uid, ids, field_name, args, context=None):
        res = {}

        if not isinstance(ids, list):
            ids = [ids]

        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.level.code or line.level.name

        return res

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
        ),

        'code': fields.char(
            'Code',
            size=32,
        ),

        'level': fields.many2one(
            'program.result.level',
            string='Level',
            required=True,
            select=True,
        ),

        'parent_action': fields.many2one(
            'program.action',
            string='Parent Action',
            select=True,
        ),

        'child_actions': fields.one2many(
            'program.action',
            'parent_result',
            string='Child Actions'
        ),

        'parent_result': fields.related(
            'parent_action',
            'parent_result',
            type='many2one',
            relation='program.result',
            string='Parent Result',
            readonly=True,
        ),

        'parent_result_search': fields.function(
            lambda **x: True,
            fnct_search=_parent_result_search,
            type='boolean',
            method=True,
        ),

        'description': fields.text(
            'Description',
        ),

        'expected_child_results': fields.text(
            'Expected Child Results',
        ),

        'planned_children': fields.function(
            _planned_children,
            type='one2many',
            obj='program.action',
            method=True,
            string='Planned Children',
        ),
        'level_code': fields.function(
            _get_level_code,
            type='char',
            method=True,
            string="Level")
    }
