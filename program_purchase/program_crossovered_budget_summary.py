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

from openerp.osv import fields, orm
from openerp.addons import decimal_precision as dp


class program_crossovered_budget_summary(orm.TransientModel):

    _name = 'program.crossovered.budget.summary'
    _description = "Budget Summary"
    _columns = {
        'budget_id': fields.many2one('crossovered.budget', 'Budget'),
        'planned_amount': fields.float(
            'Planned Amount', digits_compute=dp.get_precision('Account'),
        ),
        'practical_amount': fields.float(
            'Practical Amount', digits_compute=dp.get_precision('Account'),
        ),
        'theoretical_amount': fields.float(
            'Theoretical Amount', digits_compute=dp.get_precision('Account'),
        ),
    }
