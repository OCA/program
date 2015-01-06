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

from openerp.osv import orm, fields
from openerp.addons import decimal_precision as dp


class program_crossovered_budget_lines(orm.Model):
    """
    The financial resources budgeted by other partner organisation for a
    Result, for a specific year [i.e crossovered.budget (CB)].
    Since the crossovered.budget.line (CBL) objects are dedicated only for your
    organisation's budgets and not for partner ones, the
    program.crossovered.budget.lines (PBCL) mimics the CBL but for partners.
    """
    _name = "program.crossovered.budget.lines"
    _columns = {
        "partner_id": fields.many2one(
            "res.partner", string="Partner", required=True),
        "budget_id": fields.many2one(
            "crossovered.budget", string="Budget", required=True),
        "result_id": fields.many2one("program.result", string="Result"),
        "currency_amount": fields.float(
            string="Amount in Currency",
            digits_compute=dp.get_precision('Account'),
        ),
        "currency_id": fields.many2one('res.currency', "Currency"),
        "amount": fields.float(
            string="Amount in Account Currency",
            digits_compute=dp.get_precision('Account'),
            required=True,
        ),
    }

    def onchange_currency_amount(
            self, cr, uid, ids, currency_amount, currency_id, context=None):
        currency_pool = self.pool['res.currency']
        rate = False
        if currency_id:
            curr = currency_pool.browse(cr, uid, currency_id, context=context)
            rate = curr.rate
        return {
            'value': {
                'amount': currency_amount / (rate or 1.0),
            }
        }
