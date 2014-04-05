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


class test_program_action(TransactionCase):

    def setUp(self):
        super(test_program_action, self).setUp()
        # Clean up registries
        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()
        # Get registries
        self.user_model = self.registry("res.users")
        self.partner_model = self.registry("res.partner")
        self.program_action_model = self.registry("program.action")
        self.program_action_level_model = self.registry("program.action.level")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        parent = self.program_action_model.create(
            self.cr, self.uid, {'name': 'Test Parent'}, context=self.context)
        action_level = self.program_action_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Level',
                'depth': 0,
            }, context=self.context)
        self.vals = {
            'name': 'Test Action',
            'parent': parent,
            'code': 'TEST',
            'action_level': action_level,
            'date_from': str(time.localtime(time.time())[0] + 1) + '-01-01',
            'date_to': str(time.localtime(time.time())[0] + 1) + '-12-31',
            'description': 'Testing the program action object',
            'target_audience': 'Unittest Framework',
        }

    def test_create_program_action(self):
        self.assertTrue(self.program_action_model.create(
            self.cr, self.uid, self.vals, context=self.context))

    def test_write_program_action(self):
        program_action_id = self.program_action_model.create(
            self.cr, self.uid, self.vals, context=self.context)
        vals = {
            'name': 'Test Change Name',
        }
        self.program_action_model.write(
            self.cr, self.uid, program_action_id, vals, context=self.context)
        action = self.program_action_model.browse(
            self.cr, self.uid, program_action_id, context=self.context)
        self.assertEquals(action.name, vals['name'])
