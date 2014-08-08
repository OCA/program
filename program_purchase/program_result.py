# -*- coding: utf-8 -*-

##############################################################################
#
#    Odoo, Open Source Management Solution
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

from __future__ import division
from datetime import date, datetime

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


def prgs_cap(val, minimum=0.0, maximum=100.0):
    return min(max(val, minimum), maximum)


class program_result(orm.Model):

    _inherit = 'program.result'

    def _get_result_clb_ids(self, cr, uid, ids, budget_id, context=None):
        """Find associated accounts and descendants"""
        line_pool = self.pool['crossovered.budget.lines']

        if not ids:
            return {}

        if type(ids) is list:
            ids = ids[0]
        result = self.browse(cr, uid, ids, context=context)

        account_ids = [a.id for a in result.child_account_ids]
        return line_pool.search(
            cr, uid,
            [
                '&',
                ('analytic_account_id', 'in', account_ids),
                ('crossovered_budget_id', '=', budget_id)
            ],
            context=context
        )

    def build_budget_summary(self, cr, uid, ids, budget_id, context=None):
        line_pool = self.pool['crossovered.budget.lines']
        cbl_ids = self._get_result_clb_ids(
            cr, uid, ids, budget_id, context=context
        )
        cbls = line_pool.browse(cr, uid, cbl_ids, context=context)
        return {
            'budget_id': budget_id,
            'planned_amount': sum(i.planned_amount for i in cbls),
            'practical_amount': sum(i.practical_amount for i in cbls),
            'theoretical_amount': sum(i.theoritical_amount for i in cbls),
            'cbl_ids': cbl_ids,
        }

    def _get_budget_summaries(
            self, cr, uid, ids, name=None, args=None, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            res[result.id] = [result.build_budget_summary(budget_id.id)
                              for budget_id in result.crossovered_budget_ids]
        return res

    def _get_crossovered_budgets(self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            res[result.id] = list({
                line.crossovered_budget_id.id
                for line in result.crossovered_budget_line_ids
            })
        return res

    def _get_prgs_time(self, cr, uid, ids, name, args, context=None):
        """Return ratio of now between start and end date of result
        (capped between 0 and 100)
        """
        today = date.today()

        def get_progress(start, end):
            if not start or not end:
                return 0.0
            start = datetime.strptime(start, DEFAULT_SERVER_DATE_FORMAT).date()
            end = datetime.strptime(end, DEFAULT_SERVER_DATE_FORMAT).date()
            return prgs_cap((today - start).days / (end - start).days * 100.0)

        if type(ids) is not list:
            ids = [ids]
        return {
            i['id']: get_progress(i['date_from'], i['date_to']) for i in
            self.read(cr, uid, ids, ['date_from', 'date_to'], context=context)
        }

    def _get_prgs_budget(self, cr, uid, ids, name, args, context=None):
        """Return ratio of practical_amount between 0 and theoretical_amount of
         result (capped between 0 and 100)
        """
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            summaries = result._get_budget_summaries()[result.id]
            practical = sum(i['practical_amount'] for i in summaries)
            theoretical = sum(i['theoretical_amount'] for i in summaries)
            if theoretical == 0.0:
                res[result.id] = 0.0
            else:
                res[result.id] = prgs_cap(practical / theoretical * 100)
        return res

    def _get_prgs_appreciation(self, cr, uid, ids, name, args, context=None):
        """Return appreciation (capped between 0 and 100)"""
        if type(ids) is not list:
            ids = [ids]
        return {
            i['id']: prgs_cap(i['appreciation']) for i in
            self.read(cr, uid, ids, ['appreciation'], context=context)
        }

    def _check_appreciation(self, cr, uid, ids, context=None):
        return not any(
            self.search(
                cr, uid,
                ['|', ('appreciation', '<', 0), ('appreciation', '>', 100)],
                limit=1, context=None
            )
        )

    _columns = {
        'budget_summary_ids': fields.function(
            lambda self, *a, **kw: self._get_budget_summaries(*a, **kw),
            type="one2many",
            obj='program.crossovered.budget.summary',
            string="Budget Summaries",
            readonly=True,
        ),
        'crossovered_budget_ids': fields.function(
            lambda self, *a, **kw: self._get_crossovered_budgets(*a, **kw),
            type='many2many',
            obj='crossovered.budget',
            string='Budgets',
        ),
        'prgs_time': fields.function(
            lambda self, *a, **kw: self._get_prgs_time(*a, **kw),
            type='float',
            string='Time',
        ),
        'comment_time': fields.char(
            string='Comments',
            help='Comments for Time Progress',
        ),
        'prgs_budget': fields.function(
            # using lambda to allow overwriting
            lambda self, *a, **kw: self._get_prgs_budget(*a, **kw),
            type='float',
            string='Budget',
        ),
        'comment_budget': fields.char(
            string='Comments',
            help='Comments for Budget Progress',
        ),
        'appreciation': fields.float(
            string='Appreciation',
            track_visibility='onchange',
        ),
        'prgs_appreciation': fields.function(
            lambda self, *a, **kw: self._get_prgs_appreciation(*a, **kw),
            type='float',
            string='Appreciation',
        ),
        'comment_appreciation': fields.char(
            string='Comments',
            help='Comments for Appreciation Progress',
        ),
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return '\n\n' + _('Error! Appreciation should be between 0 and 100.')

    _constraints = [
        (_check_appreciation, _rec_message, ['appreciation']),
    ]
