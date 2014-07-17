# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010 - 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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


class program_result(orm.Model):

    _inherit = 'program.result'

    def build_budget_summary(self, cr, uid, ids, budget_id, context=None):
        budget_pool = self.pool['crossovered.budget']
        budget = budget_pool.browse(cr, uid, budget_id, context=context)
        cbls = budget.crossovered_budget_line
        return {
            'budget_id': budget.id,
            'planned_amount': sum(i.planned_amount for i in cbls),
            'practical_amount': sum(i.practical_amount for i in cbls),
            'theoretical_amount': sum(i.theoritical_amount for i in cbls),
            'progress': self.get_budget_progress(
                cr, uid, ids, budget_id, context=context
            ),
        }

    def get_budget_progress(self, cr, uid, ids, budget_id, context=None):
        budget_pool = self.pool['crossovered.budget']
        budget = budget_pool.browse(cr, uid, budget_id, context=context)
        cbls = budget.crossovered_budget_line
        practical_amount = sum(i.practical_amount for i in cbls) or 0.0
        theoretical_amount = sum(i.theoritical_amount for i in cbls) or 0.0
        if theoretical_amount == 0.00:
            return 0.00
        else:
            return practical_amount / theoretical_amount

    def _get_budget_summaries(self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            res[result.id] = [result.build_budget_summary(budget_id.id)
                              for budget_id in result.crossovered_budget_ids]
        return res

    def _get_crossovered_budgets(self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            res[result.id] = list({
                line.crossovered_budget_id.id
                for line in result.crossovered_budget_line_ids
            })
        return res

    _columns = {
        'budget_summary_ids': fields.function(
            _get_budget_summaries, type="one2many",
            obj='program.crossovered.budget.summary',
            string="Budget Summaries",
            readonly=True,
        ),
        'crossovered_budget_ids': fields.function(
            _get_crossovered_budgets, type='many2many',
            obj='crossovered.budget', string='Budgets'),
    }
