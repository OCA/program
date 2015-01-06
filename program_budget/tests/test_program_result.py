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
from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class test_program_result(test_program_result.test_program_result):

    def setUp(self):
        super(test_program_result, self).setUp()
        account_model = self.registry("account.analytic.account")
        account_post_model = self.registry("account.budget.post")
        budget_model = self.registry("crossovered.budget")
        cbl_model = self.registry("crossovered.budget.lines")

        cr, uid, context = self.cr, self.uid, self.context

        year = str(time.localtime(time.time())[0] + 1)
        date_from = year + '-01-01'
        date_to = year + '-12-31'

        self.budget_id = budget_model.create(cr, uid, {
            'name': 'Test Budget',
            'code': year,
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

        result = self.program_result_model.browse(
            cr, uid, self.result_id, context=context
        )

        self.account_analytic_id = result.account_analytic_id.id

        account_model.write(cr, uid, self.account_analytic_id, {
            'crossovered_budget_line': [(4, self.cbl_id)],
        }, context=context)

        self.program_result_model.write(
            cr, uid, self.result_id, {
                'account_analytic_id': self.account_analytic_id,
            }, context=context)

    def test_get_budget_total(self):
        cr, uid, context = self.cr, self.uid, self.context

        parent_result = self.program_result_model.browse(
            cr, uid, self.parent_id, context=context)
        self.assertEquals(parent_result.budget_total, 100.0)

        result = self.program_result_model.browse(
            cr, uid, self.result_id, context=context)
        self.assertEquals(result.budget_total, 100.0)


class test_program_result_impact_account(TransactionCase):

    def setUp(self):
        super(test_program_result_impact_account, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.partner_model = self.registry("res.partner")
        self.result_model = self.registry("program.result")
        self.budget_model = self.registry("crossovered.budget")
        self.account_model = self.registry("account.analytic.account")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context
        # Create needed objects
        from_year = time.localtime(time.time())[0] + 1
        to_year = from_year + 3
        nomenclature = self.account_model.create(cr, uid, {
            'name': 'Test Account %d - %d' % (from_year, to_year),
            'type': 'view',
        }, context=context)

        grand_parent_node = self.account_model.create(cr, uid, {
            'name': 'Test Grand Parent Program Account %d - %d' % (from_year,
                                                                   to_year),
            'type': 'view',
            'parent_id': nomenclature,
        }, context=context)
        parent_node = self.account_model.create(cr, uid, {
            'name': 'Test Parent Program Account %d - %d' % (from_year,
                                                             to_year),
            'type': 'view',
            'parent_id': grand_parent_node,
        }, context=context)
        self.alt_root_program_node = self.account_model.create(cr, uid, {
            'name': 'Test AlternativeProgram Account %d - %d' % (from_year,
                                                                 to_year),
            'type': 'view',
            'parent_id': parent_node,
        }, context=context)
        parent_id = self.result_model.create(cr, uid, {
            'name': 'Test Parent Result',
        }, context=context)
        self.alt_parent_id = self.result_model.create(cr, uid, {
            'name': 'Test Alternative Parent Result',
        }, context=context)
        # Create values
        self.vals = {
            'name': 'Test Result',
            'code': 'TEST',
            'parent_id': parent_id,
        }

    def test_create_program_result(self):
        """
        Result:
          Create Result with common fields to AA, a period and a parent
        Analytic Account (AA):
          AA is created under the parent node, under the program node of the
          parent, under the program's the budgetary period
        """
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        result_id = self.result_model.create(cr, uid, vals, context=context)
        result = self.result_model.browse(cr, uid, result_id, context=context)
        account = result.account_analytic_id
        # Common fields
        check_vals = [
            'name',
            'code',
        ]
        for i in check_vals:
            self.assertEquals(result[i], vals[i])
            self.assertEquals(account[i], result[i])
        # Parent node
        self.assertEquals(result.parent_id.account_analytic_id,
                          account.parent_id)

    def test_write_program_result(self):
        """
        Common fields:
          Result:
            Modifiable
          Analytic Account (AA):
            Modifications of Result automatically modifies the AA node
        Parent:
          Result:
            Modifiable
          Analytic Account (AA):
            The parent AA is changed
        Period
          Result:
            Modifiable
          Analytic Account (AA):
            Modifying a period, creates an AA under the parent node in
            program's node in budgetary period
        """
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        result_id = self.result_model.create(cr, uid, vals, context=context)
        # Common fields
        new_vals = {
            'name': 'changed',
            'code': 'NEW',
        }
        self.result_model.write(cr, uid, result_id, new_vals, context=context)
        result = self.result_model.browse(cr, uid, result_id, context=context)
        account = result.account_analytic_id
        for i, j in new_vals.items():
            self.assertEquals(result[i], j)
            self.assertEquals(account[i], result[i])
        # Parent node
        self.result_model.write(cr, uid, result_id, {
            'parent_id': self.alt_parent_id,
        }, context=context)
        result = self.result_model.browse(cr, uid, result_id, context=context)
        account = result.account_analytic_id
        self.assertEquals(result.parent_id.id, self.alt_parent_id)
        self.assertEquals(result.parent_id.account_analytic_id,
                          account.parent_id)

    def test_unlink_program_result(self):
        """Result cannot be deleted. Associated AA cannot be deleted"""
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        result_id = self.result_model.create(cr, uid, vals, context=context)
        result = self.result_model.browse(cr, uid, result_id, context=context)
        account_id = result.account_analytic_id.id
        self.assertRaises(except_orm, result.unlink)
        self.assertTrue(
            self.result_model.browse(cr, uid, result_id, context=context),
            "Result should not be deleted, functionality taken out.")
        self.assertTrue(
            self.account_model.browse(cr, uid, account_id, context=context),
            "Related Account should not be deleted, functionality taken out.")
