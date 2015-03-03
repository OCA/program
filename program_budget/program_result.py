# -*- coding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from openerp.osv import fields, orm
from openerp.addons import decimal_precision as dp
from openerp.tools.translate import _


class program_result(orm.Model):

    _inherit = 'program.result'

    def _get_propagatable_fields(self):
        return {
            'name',
            'code',
        }

    def _get_account_company(
            self, cr, uid, ids, name, args, context=None):
        user_pool = self.pool['res.users']
        company_id = user_pool.browse(cr, uid, uid, context=context).company_id
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            company = result.account_analytic_id.company_id or company_id
            res[result.id] = company.id
        return res

    def _get_child_account_ids(
            self, cr, uid, ids, name, args, context=None):
        """Return associated account and its children"""
        def get_child_account_ids(result_obj):
            account_ids = set()

            def recur(o):
                map(recur, o.child_ids)
                account_ids.add(o.id)

            account_obj = result_obj.account_analytic_id
            if not account_obj:
                return []
            recur(account_obj)
            return list(account_ids)

        return {
            result.id: get_child_account_ids(result)
            for result in self.browse(cr, uid, ids, context=context)
        }

    def get_child_account_ids(account_obj):
        res = set()

        def recur(o):
            map(recur, o.child_ids)
            res.add(o.id)

        recur(account_obj)
        return res

    def _get_crossovered_budget_lines(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            crossovered_budget_lines = []
            for child in result.descendant_ids + [result]:
                account = child.account_analytic_id
                if account:
                    crossovered_budget_lines += account.crossovered_budget_line
            res[result.id] = [l.id for l in crossovered_budget_lines]
        return res

    def _get_crossovered_budgets_modified_total(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        budget_ids = self._get_crossovered_budget_lines(
            cr, uid, ids, name, args, context=context)
        cbl_pool = self.pool['crossovered.budget.lines']
        for budget_id, crossovered_budget_lines_ids in budget_ids.items():
            res[budget_id] = sum(
                line.planned_amount
                for line in cbl_pool.browse(
                    cr, uid, crossovered_budget_lines_ids, context=context)
            )
        return res

    def _get_budget_total(self, cr, uid, ids, name, args, context=None):
        budgets = list()
        budgets.append(self._get_crossovered_budgets_modified_total(
            cr, uid, ids, name, args, context=context))
        return reduce(
            lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()),
            budgets)

    _columns = {
        'account_analytic_id': fields.many2one(
            'account.analytic.account', string='Analytic account',
            select=True),
        'child_account_ids': fields.function(
            lambda self, *a, **kw: self._get_child_account_ids(*a, **kw),
            obj='account.analytic.account',
            type='many2many',
            string='Analytic account',
            help="Get associated accounts and its descendants"
        ),
        'target_country_ids': fields.one2many(
            'program.result.country',
            'result_id',
            string='Target Countries',
        ),
        'target_region_ids': fields.many2many(
            'program.result.region', string='Target Regions'
        ),
        'budget_total': fields.function(
            lambda self, *args, **kw: self._get_budget_total(*args, **kw),
            string='Total',
            type='float',
            digits_compute=dp.get_precision('Account'),
            readonly=True),
        'crossovered_budget_line_ids': fields.function(
            _get_crossovered_budget_lines, type='many2many',
            obj='crossovered.budget.lines', string='Budget Lines'),
        'company_id': fields.function(
            _get_account_company, type='many2one', relation='res.company',
            string='Company', readonly=True),
        'currency_id': fields.related(
            'company_id', 'currency_id', type='many2one',
            relation='res.currency', string='Currency', readonly=True),
        'crossovered_budgets_modified_total': fields.function(
            _get_crossovered_budgets_modified_total, type='float',
            digits_compute=dp.get_precision('Account'), readonly=True,
            string="Total Company Budget"),
    }

    def _get_parent_account_id(self, cr, uid, ids, vals=None, context=None):
        """ Return the parent account analytic id."""
        if not ids and not vals:
            return False
        if not vals:
            vals = self.read(
                cr, uid, ids, ['parent_id'],
                context=context
            )[0]
        parent_id = vals.get('parent_id')
        if not parent_id:
            return False
        parent_id = self.browse(cr, uid, parent_id, context=context)
        return (
            parent_id.account_analytic_id and
            parent_id.account_analytic_id.id
        )

    def create(self, cr, uid, vals, context=None):
        """ Create a program.result

        Create an analytic account under under the root node
        of the budgetary period or under the parent result,
        if specified. """

        if context is None:
            context = {}

        if context.get('account_written'):
            return super(program_result, self).create(
                cr, uid, vals, context=context
            )

        if not vals.get('result_level_id'):
            vals['result_level_id'] = self._result_level_id(
                cr, uid, parent_id=vals.get('parent_id'), context=context
            )

        vals['account_analytic_id'] = self._create_related_account(
            cr, uid, vals, context=context)

        return super(program_result, self).create(
            cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """ Update the program.result

        Propagate the changes to the account analytic that is
        tied to this program result.

        If the parent result is changed, move the linked account
        analytic as well. """

        if context is None:
            context = {}

        if type(ids) not in (list, ):
            ids = [ids]

        res = super(program_result, self).write(
            cr, uid, ids, vals, context=context)

        if context.get('account_written'):
            return res
        account_pool = self.pool.get('account.analytic.account')
        for result in self.browse(cr, uid, ids, context=context):
            if not result.account_analytic_id:
                prop_vals = dict(self.read(
                    cr, uid, result.id,
                    self._get_propagatable_fields(),
                    context=context).items() + vals.items())
                prop_vals['result_level_id'] = result.result_level_id.id
                account_id = self._create_related_account(
                    cr, uid, prop_vals, context=context)
                result.write({'account_analytic_id': account_id},
                             context=context)
                result = result.browse(context=context)[0]

            propagated_fields = {
                i: j for i, j in vals.items()
                if i in self._get_propagatable_fields()
            }

            if 'parent_id' in vals:
                parent_account_id = self._get_parent_account_id(
                    cr, uid, ids, dict(
                        parent_id=result.parent_id.id,
                    ), context=context)
                propagated_fields['parent_id'] = parent_account_id

            if propagated_fields:
                account_pool.write(
                    cr, uid, result.account_analytic_id.id,
                    propagated_fields,
                    context=dict(context, result_written=True))

        return res

    def unlink(self, cr, uid, ids, context=None):
        raise orm.except_orm(_('Error'),
                             _('Deletion of Results has been disabled'))

    def _create_related_account(self, cr, uid, vals, context=None):
        parent_account_id = self._get_parent_account_id(
            cr, uid, ids=None, vals=vals, context=context
        )

        account_pool = self.pool.get('account.analytic.account')
        propagated_fields = {
            i: j
            for i, j in vals.items() if i in self._get_propagatable_fields()
        }

        return account_pool.create(
            cr, uid, dict(propagated_fields.items() + {
                'name': vals.get('name', False),
                'code': vals.get('code', False),
                'type': 'view',
                'parent_id': parent_account_id,
            }.items()),
            context=dict(context, result_written=True),
        )
