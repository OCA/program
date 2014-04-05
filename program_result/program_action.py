# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Savoir-faire Linux (<www.savoirfairelinux.com>).
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
from openerp.tools.translate import _


class program_action(orm.Model):

    _inherit = 'program.action'

    def _child_results(self, cr, uid, ids, name, arg, context=None):
        # FIXME Needs to be tweaked as per new diagrams!

        if isinstance(ids, (int, long)):
            ids = [ids]

        res = {}

        result_pool = self.pool.get('program.result')

        for action in self.browse(cr, uid, ids, context=context):
            results = [result.id for result in action.results]
            child_result_ids = result_pool.search(
                cr, uid, [('parent_result', 'in', results)], context=context)

            res[action.id] = child_result_ids

        return res

    def action_open_child_results(self, cr, uid, ids, context=None):
        action = self.browse(cr, uid, ids, context=context)[0]
        child_results = [r.id for r in action.child_results]
        return {
            'name': _('Child Results'),
            'res_model': 'program.result',
            'view_mode': 'tree',
            'view_type': 'tree',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'domain': "[('id','in'," + str(child_results) + ")]",
            'target': 'new',
            'res_id': ids[0],
            'context': context,
        }

    _columns = {
        'results': fields.one2many(
            'program.result', 'parent_action', string='Results'),
        'parent_result': fields.many2one(
            'program.result', string='Parent Result', select=True),
        'child_results': fields.function(
            _child_results, type='one2many', obj='program.result', method=True,
            string='Child Results'),
        'parent_expected_child_results': fields.related(
            'parent_result', 'expected_child_results', type='text',
            string='Parent Expected Child Results', readonly=True),
    }
