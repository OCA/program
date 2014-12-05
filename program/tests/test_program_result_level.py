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


class test_program_result_level(TransactionCase):

    def setUp(self):
        super(test_program_result_level, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.program_result_level_model = self.registry("program.result.level")
        self.spec_model = self.registry("program.result.validation.spec")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)

        result_level_1_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 1',
            }, context=self.context)
        self.spec_model.create(
            self.cr, self.uid, {
                'level_id': result_level_1_id,
                'group_id': 1,
                'states': "a,b,c",
            }, context=self.context
        )
        result_level_2_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 2',
                'parent_id': result_level_1_id,
            }, context=self.context)
        result_level_3_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Level 3',
                'parent_id': result_level_2_id,
            }, context=self.context)
        result_level_4_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Orphan Level',
            }, context=self.context)
        self.result_level_1 = self.program_result_level_model.browse(
            self.cr, self.uid, result_level_1_id, context=self.context
        )
        self.result_level_2 = self.program_result_level_model.browse(
            self.cr, self.uid, result_level_2_id, context=self.context
        )
        self.result_level_3 = self.program_result_level_model.browse(
            self.cr, self.uid, result_level_3_id, context=self.context
        )
        self.result_level_4 = self.program_result_level_model.browse(
            self.cr, self.uid, result_level_4_id, context=self.context
        )

    def test_parents(self):
        self.assertFalse(self.result_level_1.parent_id)
        self.assertEqual(self.result_level_2.parent_id, self.result_level_1)
        self.assertEqual(self.result_level_3.parent_id, self.result_level_2)
        self.assertFalse(self.result_level_4.parent_id)

    def test_children(self):
        self.assertEqual(self.result_level_1.child_id, [self.result_level_2])
        self.assertEqual(self.result_level_2.child_id, [self.result_level_3])
        self.assertEqual(self.result_level_3.child_id, [])
        self.assertEqual(self.result_level_4.child_id, [])

    def test_depth(self):
        self.assertEqual(self.result_level_1.depth, 1)
        self.assertEqual(self.result_level_2.depth, 2)
        self.assertEqual(self.result_level_3.depth, 3)
        self.assertEqual(self.result_level_4.depth, 1)

    def test_root(self):
        self.assertEqual(self.result_level_1.chain_root, self.result_level_1)
        self.assertEqual(self.result_level_2.chain_root, self.result_level_1)
        self.assertEqual(self.result_level_3.chain_root, self.result_level_1)
        self.assertEqual(self.result_level_4.chain_root, self.result_level_4)

    def test_tail(self):
        self.assertEqual(self.result_level_1.chain_tail, self.result_level_3)
        self.assertEqual(self.result_level_2.chain_tail, self.result_level_3)
        self.assertEqual(self.result_level_3.chain_tail, self.result_level_3)
        self.assertEqual(self.result_level_4.chain_tail, self.result_level_4)

    def test_orphan(self):
        # Clear the parent_id field, making this a top level
        self.result_level_2.write({'parent_id': False})
        self.result_level_2.refresh()
        self.assertEqual(self.result_level_2.depth, 1)
        self.assertEqual(self.result_level_4.depth, 1)

    def test_reverse(self):
        # Change parents by reversing the chain
        self.result_level_3.write({'parent_id': False})
        self.result_level_3.refresh()
        self.result_level_2.write({'parent_id': self.result_level_3.id})
        self.result_level_2.refresh()
        self.result_level_1.write({'parent_id': self.result_level_2.id})
        self.result_level_1.refresh()
        self.assertEqual(self.result_level_1.depth, 3)
        self.assertEqual(self.result_level_2.depth, 2)
        self.assertEqual(self.result_level_3.depth, 1)
        # Check bubbling up of spec_ids
        self.assertTrue(self.result_level_3.validation_spec_ids)
        self.assertFalse(self.result_level_2.validation_spec_ids)
        self.assertFalse(self.result_level_1.validation_spec_ids)
