# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
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

    def _get_account_company(
            self, cr, uid, ids, name, args, context=None):
        user_pool = self.pool['res.users']
        company_id = user_pool.browse(cr, uid, uid, context=context).company_id
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            company = result.account_analytic_id.company_id or company_id
            res[result.id] = company.id
        return res

    def _get_crossovered_budgets(self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            crossovered_budget_lines = []
            for child in result.descendant_ids + [result]:
                account = child.account_analytic_id
                if account:
                    crossovered_budget_lines += account.crossovered_budget_line
            res[result.id] = [l.id for l in crossovered_budget_lines]
        return res

    def _get_crossovered_budgets_modified_total(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        budget_ids = self._get_crossovered_budgets(
            cr, uid, ids, name, args, context=context)
        cbl_pool = self.pool['crossovered.budget.lines']
        for budget_id, crossovered_budget_lines_ids in budget_ids.items():
            res[budget_id] = sum(
                line.planned_amount
                for line in cbl_pool.browse(
                    cr, uid, crossovered_budget_lines_ids, context=context)
            )
        return res

    def _get_foreign_budgets_total(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            amount = sum(sum(l.amount for l in child.foreign_budget_lines)
                         for child in result.descendant_ids + [result])
            res[result.id] = amount
        return res

    def _get_budget_total(self, cr, uid, ids, name, args, context=None):
        budgets = list()
        budgets.append(self._get_crossovered_budgets_modified_total(
            cr, uid, ids, name, args, context=context))
        budgets.append(self._get_foreign_budgets_total(
            cr, uid, ids, name, args, context=context))
        return reduce(
            lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()),
            budgets)

    _columns = {
        'account_analytic_id': fields.many2one(
            'account.analytic.account', string='Analytic account',
            select=True),
        'target_country': fields.many2many(
            'res.country', string='Target Country'
        ),
        'target_region': fields.many2many(
            'program.result.region', string='Target Region'
        ),
        'budget_total': fields.function(
            _get_budget_total, string='Total', type='float', digits=(12, 0),
            readonly=True),
        'crossovered_budget_ids': fields.function(
            _get_crossovered_budgets, type='many2many',
            obj='crossovered.budget.lines', string='Budgets'),
        'company_id': fields.function(
            _get_account_company, type='many2one', relation='res.company',
            string='Company', readonly=True),
        'currency_id': fields.related(
            'company_id', 'currency_id', type='many2one',
            relation='res.currency', string='Currency', readonly=True),
        'crossovered_budgets_modified_total': fields.function(
            _get_crossovered_budgets_modified_total, type='float',
            digits = (12, 0), readonly=True, string="Total Company Budget"),
        'foreign_budget_lines': fields.one2many(
            'program.crossovered.budget.lines', 'result_id',
            string='Foreign Budgets'),
        'foreign_budget_total': fields.function(
            _get_foreign_budgets_total, type='float',
            digits=(12, 0), readonly=True, string="Total Foreign Budgets"),
    }
