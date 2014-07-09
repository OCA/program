# -*- encoding: utf-8 -*-
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

import time
from openerp.addons.program.tests import test_program_result


class test_program_result(test_program_result.test_program_result):

    def setUp(self):
        super(test_program_result, self).setUp()
        partner_model = self.registry("res.partner")
        account_model = self.registry("account.analytic.account")
        account_post_model = self.registry("account.budget.post")
        budget_model = self.registry("crossovered.budget")
        cbl_model = self.registry("crossovered.budget.lines")
        pcbl_model = self.registry("program.crossovered.budget.lines")

        cr, uid, context = self.cr, self.uid, self.context

        year = str(time.localtime(time.time())[0] + 1)
        date_from = year + '-01-01'
        date_to = year + '-12-31'

        self.budget_id = budget_model.create(cr, uid, {
            'name': 'Test Budget',
            'code': year,
            'year': year,
            'date_from': date_from,
            'date_to': date_from,
        }, context=context)

        general_budget_id = account_post_model.create(cr, uid, {
            'name': 'TEST',
            'code': 'TEST',
        }, context=context)

        self.cbl_id = cbl_model.create(cr, uid, {
            'date_from': date_from,
            'date_to': date_to,
            'general_budget_id': general_budget_id,
            'crossovered_budget_id': self.budget_id,
            'planned_amount': 100.0,
        }, context=context)

        self.account_analytic_id = account_model.create(cr, uid, {
            'name': 'test account',
            'crossovered_budget_line': [(4, self.cbl_id)],
        }, context=context)

        self.foreign_budget_lines = pcbl_model.create(cr, uid, {
            'partner_id': partner_model.create(cr, uid, {'name': 'test'},
                                               context=context),
            'budget_id': self.budget_id,
            'result_id': self.result_id,
            'amount': 20.0,
        }, context=self.context)

        self.program_result_model.write(
            cr, uid, self.result_id, {
                'account_analytic_id': self.account_analytic_id,
            }, context=context)

    def test_get_crossovered_budgets(self):
        cr, uid, context = self.cr, self.uid, self.context
        parent_result = self.program_result_model.browse(
            cr, uid, self.parent_id, context=context)
        cb_ids = parent_result.crossovered_budget_ids
        self.assertEquals([i.id for i in cb_ids], [self.cbl_id])

    def test_get_budget_total(self):
        cr, uid, context = self.cr, self.uid, self.context

        parent_result = self.program_result_model.browse(
            cr, uid, self.parent_id, context=context)
        self.assertEquals(parent_result.budget_total, 120.0)

        result = self.program_result_model.browse(
            cr, uid, self.result_id, context=context)
        self.assertEquals(result.budget_total, 120.0)

    def test_get_account_company_label(self):
        cr, uid, context = self.cr, self.uid, self.context
        parent_result = self.program_result_model.browse(
            cr, uid, self.parent_id, context=context)
        users_pool = self.registry("res.users")
        company = users_pool.browse(cr, uid, uid, context=context).company_id
        name = company.name_get()[0][1] + u" :"
        label = parent_result.company_label
        self.assertEquals(label.strip(), name.strip())
