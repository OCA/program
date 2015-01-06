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

import time
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
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        self.parent_id = self.program_result_model.create(
            self.cr, self.uid, {'name': 'Test Parent'}, context=self.context)
        result_level_id = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Level',
            }, context=self.context)
        self.vals = {
            'name': 'Test Result',
            'parent_id': self.parent_id,
            'code': 'TEST',
            'result_level_id': result_level_id,
            'date_from': str(time.localtime(time.time())[0] + 1) + '-01-01',
            'date_to': str(time.localtime(time.time())[0] + 1) + '-12-31',
            'description': 'Testing the program result object',
        }
        self.result_id = self.program_result_model.create(
            self.cr, self.uid, self.vals, context=self.context)

    def test_write_program_result(self):
        vals = {
            'name': 'Test Change Name',
        }
        self.program_result_model.write(
            self.cr, self.uid, self.result_id, vals, context=self.context)
        result = self.program_result_model.browse(
            self.cr, self.uid, self.result_id, context=self.context)
        self.assertEquals(result.name, vals['name'])

    def test_name_get_program_result(self):
        self.assertEqual(
            self.program_result_model.name_get(
                self.cr, self.uid, self.result_id, context=self.context
            )[0][1],
            "%s-%s" % (self.vals['code'], self.vals['name'])
        )
        vals = {
            'code': False,
        }
        self.program_result_model.write(
            self.cr, self.uid, self.result_id, vals, context=self.context
        )
        self.assertEqual(
            self.program_result_model.name_get(
                self.cr, self.uid, self.result_id, context=self.context
            )[0][1],
            self.vals['name']
        )

    def test_get_descendants_program_result(self):
        parent_result = self.program_result_model.browse(
            self.cr, self.uid, self.parent_id, context=self.context)
        self.assertEqual(
            [r.id for r in parent_result.descendant_ids],
            [self.result_id],
        )
