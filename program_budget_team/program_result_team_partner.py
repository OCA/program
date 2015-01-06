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
import openerp.addons.decimal_precision as dp


class program_result_team_partner(orm.Model):

    _inherit = 'program.result.team.partner'
    _columns = {
        'contribution': fields.float(
            'Contribution',
            digits_compute=dp.get_precision('Account'),
        ),
        'currency_id': fields.many2one(
            'res.currency',
            'Currency',
            required=True,
        ),
        'amount': fields.function(
            lambda self, *args, **kwargs: self._amount(*args, **kwargs),
            type='float',
            multi=True,
            digits_compute=dp.get_precision('Account'),
            string='Amount company currency'
        ),
    }

    def _amount(self, cr, uid, ids, field_name=None, args=None, context=None):
        context = context or {}

        if not isinstance(ids, list):
            ids = [ids]

        res = {}

        company_rate = self.pool['res.users'].browse(
            cr, uid, uid, context=context).company_id.currency_id.rate

        for partner in self.browse(cr, uid, ids, context=context):
            try:
                rate = company_rate / partner.currency_id.rate
                amount = partner.contribution * rate
            except (ZeroDivisionError, TypeError):
                amount = False
            res[partner.id] = {
                'amount': amount,
            }

        return res
