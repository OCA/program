# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
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
###############################################################################

import time
from openerp.tests.common import TransactionCase
from openerp.osv.orm import except_orm


class test_account_impact_program_result(TransactionCase):

    def setUp(self):
        super(test_account_impact_program_result, self).setUp()
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
        self.parent_node = self.account_model.create(cr, uid, {
            'name': 'Test Parent Program Account %d - %d' % (from_year,
                                                             to_year),
            'type': 'view',
            'parent_id': grand_parent_node,
        }, context=context)
        self.root_program_node = self.account_model.create(cr, uid, {
            'name': 'Test Program Account %d - %d' % (from_year, to_year),
            'type': 'view',
            'parent_id': self.parent_node,
        }, context=context)
        parent_id = self.result_model.create(cr, uid, {
            'name': 'Test Parent Result',
        }, context=context)
        bellow_root_account_id = self.result_model.browse(
            cr, uid, parent_id, context=context
        ).account_analytic_id.id
        self.account_model.write(cr, uid, bellow_root_account_id, {
            'name': 'Test Child of Root Node Account',
            'type': 'view',
            'parent_id': self.root_program_node,
        }, context=context)
        # bellow_root_account_id = self.account_model.create(cr, uid, {
        #     'name': 'Test Child of Root Node Account',
        #     'type': 'view',
        #     'parent_id': self.root_program_node,
        # }, context=context)
        self.alt_parent_id = self.account_model.create(cr, uid, {
            'name': 'Test Alternative Parent Account',
            'type': 'view',
            'parent_id': self.root_program_node,
        }, context=context)
        # Create values
        self.vals = {
            'name': 'Test Account',
            'code': 'TEST',
            'type': 'view',
            'parent_id': bellow_root_account_id,
        }

    def test_create_account(self):
        """
        Analytic Account (AA):
          Create an Analytic Account
        Result:
          If under, or indirectly under root program node type of Account:
            Creates a Result with period pre-determined (if there are many
            crossovered.budget.period for this node, take the newest).
            Pre-fill parent and common fields
          Else do not create a result
        """
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        account_id = self.account_model.create(cr, uid, vals, context=context)
        account = self.account_model.browse(cr, uid, account_id,
                                            context=context)
        result_ids = self.result_model.search(
            cr, uid, [('account_analytic_id', '=', account_id)],
            context=context)
        self.assertGreaterEqual(len(result_ids), 1,
                                "Result linked to Analytic Account not found")
        self.assertEquals(len(result_ids), 1,
                          "Result - analytic account relation should be "
                          "one-to-one")
        result = self.result_model.browse(cr, uid, result_ids[0],
                                          context=context)
        # Common fields
        check_vals = [
            'name',
            'code',
        ]
        for i in check_vals:
            self.assertEquals(account[i], vals[i])
            self.assertEquals(result[i], account[i])
        # Parent node
        self.assertEquals(account.parent_id,
                          result.parent_id.account_analytic_id)
        # Parent account is root node
        orphan_account_id = self.account_model.create(
            cr, uid, dict(vals, parent_id=self.root_program_node),
            context=context)
        orphan_result_ids = self.result_model.search(
            cr, uid, [('account_analytic_id', '=', orphan_account_id)],
            context=context)
        self.assertFalse(orphan_result_ids,
                         "An account directly under a root program node "
                         "with no program results should not generate any.")
        # Account is root node or above
        self.assertEquals(len(self.result_model.search(
            cr, uid, [('account_analytic_id', '=', self.root_program_node)],
            context=context)), 0,
            "A root program node shouldn't have a Result linked to it")
        self.assertEquals(len(self.result_model.search(
            cr, uid, [('account_analytic_id', '=', self.parent_node)],
            context=context)), 0,
            "An Account higher up the chain of a root program node shouldn't "
            "have a Result linked to it")

    def test_write_account(self):
        """
        Common fields:
          Analytic Account (AA):
            Modifiable
          Result:
            Modifications of Result automatically modifies the Result
        Parent:
          Analytic Account (AA):
            Modifiable
          Result:
            The parent Result is changed
        """
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        account_id = self.account_model.create(cr, uid, vals, context=context)
        # Common fields
        new_vals = {
            'name': 'changed',
            'code': 'NEW',
        }
        self.account_model.write(cr, uid, account_id, new_vals,
                                 context=context)
        account = self.account_model.browse(cr, uid, account_id,
                                            context=context)
        result_id = self.result_model.search(
            cr, uid, [('account_analytic_id', '=', account_id)],
            context=context)[0]
        result = self.result_model.browse(cr, uid, result_id, context=context)
        for i, j in new_vals.items():
            self.assertEquals(account[i], j)
            self.assertEquals(result[i], account[i])
        # Parent node
        self.account_model.write(cr, uid, account_id, {
            'parent_id': self.alt_parent_id,
        }, context=context)
        account = self.account_model.browse(cr, uid, account_id,
                                            context=context)
        self.assertEquals(account.parent_id.id, self.alt_parent_id)

    def test_unlink_program_result(self):
        """Analytic Account cannot be deleted if linked to Result"""
        cr, uid, vals, context = self.cr, self.uid, self.vals, self.context
        account_id = self.account_model.create(cr, uid, vals, context=context)
        account = self.account_model.browse(cr, uid, account_id,
                                            context=context)
        result_id = self.result_model.search(
            cr, uid, [('account_analytic_id', '=', account_id)],
            context=context)[0]
        self.assertRaises(except_orm, account.unlink)
        self.assertTrue(
            self.account_model.browse(cr, uid, account_id, context=context),
            "Account should not be deleted, functionality taken out.")
        self.assertTrue(
            self.result_model.browse(cr, uid, result_id, context=context),
            "Related Result should not be deleted, functionality taken out.")
