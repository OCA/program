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


class res_partner(orm.Model):

    _inherit = 'res.partner'

    def _is_not_employee_search(self, cr, uid, obj, name, args, context=None):
        """Get all res.partner who aren't companies and don't have employees"""

        if context is None:
            context = {}

        partner_pool = self.pool.get('res.partner')
        partner_ids = partner_pool.search(
            cr, uid, [('is_company', '=', False)], context=context)
        partners = partner_pool.browse(cr, uid, partner_ids, context=context)

        res = []

        for partner in partners:
            ok = True
            users = partner.user_ids
            for user in users:
                if user.employee_ids:
                    ok = False
                    break
            if ok:
                res.append(partner.id)

        return [('id', 'in', res)]

    _columns = {
        'is_not_employee': fields.function(
            lambda **x: True,
            fnct_search=_is_not_employee_search,
            type='boolean',
            string='Not Employee',
            method=True,
        ),
    }
