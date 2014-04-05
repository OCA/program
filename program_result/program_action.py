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
from mako.template import Template


class program_action(orm.Model):

    _inherit = 'program.action'

    def _child_results(self, cr, uid, ids, name, arg, context=None):
        # FIXME Needs to be tweaked as per new diagrams!

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')

        for action in self.browse(cr, uid, ids, context=context):
            results = [result.id for result in action.results]
            child_result_ids = result_pool.search(
                cr, uid, [('parent_result', 'in', results)], context=context)

            res[action.id] = child_result_ids

        return res

    def _child_results_list(self, cr, uid, ids, name, arg, context=None):

        template = Template("""\
<ul style="list-style-type: none;margin-left: -130px;">
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
      <div class="oe_form_field oe_form_field_text">
        <span class="oe_form_text_content">${result['expected']}</span>
      </div>
    % endif
  % endif
  </li>
% endfor
</ul>""")

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')

        for action in self.browse(cr, uid, ids, context=context):
            vals = []
            for result in action.results:
                val = {
                    'result': result.name_get()[0][1],
                    'expected': result.expected_child_results,
                    'childs': []
                }
                child_result_ids = result_pool.search(
                    cr, uid, [('parent_result', '=', result.id)],
                    context=context)
                if not child_result_ids:
                    continue
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
            'program.result', 'parent_action', string='Results'),
        'parent_result': fields.many2one(
            'program.result', string='Parent Result', select=True),
        'child_results': fields.function(
            _child_results, type='one2many', obj='program.result', method=True,
            string='Child Results'),
        'child_results_list': fields.function(
            _child_results_list, type='html', method=True,
            string='Child Results'),
        'parent_expected_child_results': fields.related(
            'parent_result', 'expected_child_results', type='text',
            string='Parent Expected Child Results', readonly=True),
    }
