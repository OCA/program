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
        self.program_result_model = self.registry("program.result")
        self.program_result_level_model = self.registry("program.result.level")
        # Get context
        self.context = self.user_model.context_get(self.cr, self.uid)
        cr, uid, context = self.cr, self.uid, self.context
        # Create needed objects
        parent__level = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Parent Level',
                'depth': 0,
            }, context=self.context)
        parent_action = self.program_action_model.create(cr, uid, {
            'name': 'Test Parent Action',
        }, context=context)
        self.parent_result = self.program_result_model.create(cr, uid, {
            'name': 'Test Parent Result',
            'parent_action': parent_action,
            'result_level': parent__level,
        }, context=context)
        child__level = self.program_result_level_model.create(
            self.cr, self.uid, {
                'name': 'Test Child Level',
                'depth': 0,
            }, context=self.context)
        self.child_action = self.program_action_model.create(cr, uid, {
            'name': 'Test Child Action',
        }, context=context)
        self.child_result = self.program_result_model.create(cr, uid, {
            'name': 'Test Child Result',
            'parent_action': self.child_action,
            'result_level': child__level,
        }, context=context)

    def test_add_parent_result(self):
        cr, uid, context = self.cr, self.uid, self.context
        self.program_action_model.write(cr, uid, self.child_action, {
            'parent_result': self.parent_result,
        }, context=context)
        sql = """\
SELECT id, parent_result
FROM %s
WHERE id = %%s
""" % (self.program_result_model._table)
        cr.execute(sql, [self.child_result])
        pre_res = dict(zip(('id', 'parent_result'), cr.fetchone()))
        actual_res = self.program_result_model.read(
            cr, uid, self.child_result, ['parent_result'], context=context)
        cr.execute(sql, [self.child_result])
        post_res = dict(zip(('id', 'parent_result'), cr.fetchone()))
        self.assertEquals(pre_res, actual_res,
                          "parent_result was not initialized prior to reading")
        self.assertEquals(pre_res, post_res,
                          "parent_result has changed while reading")
