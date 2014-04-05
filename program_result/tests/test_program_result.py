# -*- encoding: utf-8 -*-
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

from openerp.tests.common import TransactionCase


class test_program_result(TransactionCase):

    def setUp(self):
        super(test_program_result, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.partner_model = self.registry("res.partner")
        self.program_result_model = self.registry("program.result")
        self.program_result_level_model = self.registry("program.result.level")
        self.program_action_model = self.registry("program.action")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        # Create needed objects
        result_level = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Level',
                'depth': 0,
            }, context=self.context)
        self.vals = {
            'name': 'Test Result',
            'code': 'TEST',
            'result_level': result_level,
            'description': 'Testing the program result object',
        }

    def test_create_program_result(self):
        self.assertTrue(self.program_result_model.create(
            self.cr, self.uid, self.vals, context=self.context))

    def test_write_program_result(self):
        program_result_id = self.program_result_model.create(
            self.cr, self.uid, self.vals, context=self.context)
        vals = {
            'code': 'TEST2',
        }
        self.program_result_model.write(
            self.cr, self.uid, program_result_id, vals, context=self.context)
        action = self.program_result_model.browse(
            self.cr, self.uid, program_result_id, context=self.context)
        self.assertEquals(action.code, vals['code'])

    def test_get_child_results(self):
        # Test with no association
        root_result_id = self.program_result_model.create(
            self.cr, self.uid, self.vals, context=self.context)
        child_result_level_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Child Level',
                'depth': 0,
            }, context=self.context)
        child_result_id = self.program_result_model.create(
            self.cr, self.uid, {
                'name': 'Test Result Child',
                'result_level': child_result_level_id,
            }, context=self.context)
        children_ids = self.program_result_model._get_child_results(
            self.cr, self.uid, root_result_id, '', context=self.context)
        self.assertEqual(children_ids[root_result_id], [],
                         "Expected empty child list, got %s"
                         % children_ids[root_result_id])
        # Test with direct action association
        root_action_id = self.program_action_model.create(self.cr, self.uid, {
            'name': 'Test Root action',
        }, context=self.context)
        child_action_id = self.program_action_model.create(self.cr, self.uid, {
            'name': 'Test Child action',
            'parent': root_action_id,
            'parent_result': root_result_id,
        }, context=self.context)
        self.program_result_model.write(self.cr, self.uid, root_result_id, {
            'parent_action': root_action_id,
        }, context=self.context)
        self.program_result_model.write(self.cr, self.uid, child_result_id, {
            'parent_action': child_action_id,
        }, context=self.context)
        children_ids = self.program_result_model._get_child_results(
            self.cr, self.uid, root_result_id, '', context=self.context)
        self.assertIn(child_result_id, children_ids[root_result_id],
                      "Expected a child (id:%d) in list, got %s"
                      % (child_result_id, children_ids[root_result_id]))
