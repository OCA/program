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
from openerp.tools.translate import _

class program_result(orm.Model):

    _inherit = 'program.result'

    _columns = {
        'result_indicator_id': fields.one2many(
            'result.indicator',
            'result_id',
            'Result Indicator',
        )
    }

class program_action(orm.Model):
    
    _inherit = 'program.action'

    def _child_results_list(self, cr, uid, ids, name, arg, context=None):
        template = Template(
"""<ul style="list-style-type: none;margin-left: -130px;">
% for result in values:
  <h3>${result['result'].name}</h3>
<table class="oe_form_group">
  <tbody>
    <tr class="oe_form_group_row">
      <td class="oe_form_group_cell">
        <div class="oe_form_field oe_form_field_many2many">
          <div class="oe_list oe_view">
            <table class="oe_list_content">
              <thead>
                <tr class="oe_list_header_columns">
                  <th class="oe_list_header_char null">
                    ${_('Indicator')}
                  </th>
                  <th class="oe_list_header_char null">
                    ${_('Initial value')}
                  </th>
                  <th class="oe_list_header_char null">
                    ${_('Target value')}
                  </th>
                  <th class="oe_list_header_char null">
                    ${_('Value')}
                  </th>
                </tr>
              </thead>
              <tbody>
                % for indicator in result['indicators']:
                <tr data-id="${indicator.id}" style>
                  <td class="oe_list_field_cell oe_list_field_char oe_required">
                    ${indicator.indicator_id.name}
                  </td>
                  <td class="oe_list_field_cell oe_list_field_char oe_required">
                    ${indicator.value_initial}
                  </td>
                  <td class="oe_list_field_cell oe_list_field_char oe_required">
                    ${indicator.value_target}
                  </td>
                  <td class="oe_list_field_cell oe_list_field_char oe_required">
                    ${indicator.value}
                  </td>
                </tr>
                % endfor
              </tbody>
            </table>
          </div>
        </div>
      </td>
    </tr>
  </tbody>
</table>
  <br />
% endfor
       
</ul>""")

        if context is None:
            context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')
        indicator_pool = self.pool.get('result.indicator')

        vals = []
        for action in self.browse(cr, uid, ids, context=context):
            
            for result in action.results:
                
                indicator_values = []

                indicator_ids = indicator_pool\
                    .search(cr, uid,[('result_id', '=', result.id)],
                            context=context)

                indicators = indicator_pool.browse(cr, uid, indicator_ids,
                                                   context=context)
                
                for indicator in indicators:
                    indicator_values.append(indicator)
                vals.append({
                    'result': result,
                    'indicators': indicator_values
                })

            res[action.id] = template.render(values=vals,
                                             _=_)

        return res


    _columns = {
        'child_results_list': fields.function(
            _child_results_list,
            type='html',
            method=True,
            string='Child Results',
        ),
    }

class result_indicator(orm.Model):

    _name = 'result.indicator'

    def change_indicator(self, cr, uid, ids, indicator_id, context=None):
        indicator = self.pool.get('program.indicator').browse(cr, uid, indicator_id, context=context)

        return {
            'value': {
                'verification_means': indicator.verification_means,
                'risk_hypothesis': indicator.risk_hypothesis
            }
        }

    _defaults = {
        'state': 'draft',
    }

    _columns = {

        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('pending', 'Pending'),
                ('open', 'Open'),
                ('submitted', 'Submitted'),
                ('validated', 'Validated'),
                ('cancel', 'Cancelled'),
            ],
            'Status',
            select=True,
            required=True,
            readonly=True
        ),

        'indicator_id': fields.many2one(
            'program.indicator',
            'Indicator',
            required=True,
        ),

        'action_id': fields.related(
            'result_id',
            'parent_action',
            type="many2one",
            relation="program.action",
            string="Action",
            store=True
        ),

        'result_id': fields.many2one(
            'program.result',
            'Result',
            required=True,
        ),

        'mandatory': fields.boolean(
            'Mandatory'
        ),

        'verification_means': fields.text(
            'Verification means'
        ),

        'risk_hypothesis': fields.text(
            'Risk hypothesis'
        ),

        'value_initial': fields.char(
            'Initial value',
            size=128,
        ),

        'value_target': fields.char(
            'Target value',
            size=128,
        ),

        'value': fields.char(
            'Value',
            size=128,
        ),

        'value_date': fields.datetime(
            'Date'
        ),

        'partner_id': fields.many2one(
            'res.partner',
            'User',
        ),

        'comment': fields.text(
            'Comment',
        ),
        
    }


class program_indicator(orm.Model):

    _name = 'program.indicator'

    _columns = {
        'name': fields.char(
            'Name',
            required=True,
            select=True,
        ),

        'generic': fields.boolean(
            'Generic',
            required=False
        ),

        'verification_means': fields.text(
            'Verification means'
        ),

        'risk_hypothesis': fields.text(
            'Risk Hypothesis'
        ),

    }

class program_result(orm.Model):
    
    _inherit = 'program.result'

    
