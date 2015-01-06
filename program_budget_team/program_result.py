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


class program_result(orm.Model):

    _inherit = 'program.result'

    def _get_foreign_budgets_total(
            self, cr, uid, ids, name, args, context=None):
        res = {}
        for result in self.browse(cr, uid, ids, context=context):
            amount = sum(sum(l.amount for l in child.team_partner_ids)
                         for child in result.descendant_ids + [result])
            res[result.id] = amount
        return res

    def _get_budget_total(self, cr, uid, ids, name, args, context=None):
        budgets = list()
        budgets.append(super(program_result, self)._get_budget_total(
            cr, uid, ids, name, args, context=context))
        budgets.append(self._get_foreign_budgets_total(
            cr, uid, ids, name, args, context=context))
        return reduce(
            lambda x, y: dict((k, v + y[k]) for k, v in x.iteritems()),
            budgets)

    _columns = {
        'foreign_budget_total': fields.function(
            lambda self, *args, **kwargs: self._get_foreign_budgets_total(
                *args, **kwargs
            ),
            type='float',
            digits_compute=dp.get_precision('Account'),
            readonly=True,
            string="Total Foreign Budgets",
        ),
    }
