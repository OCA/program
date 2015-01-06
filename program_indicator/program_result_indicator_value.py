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

import time

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class program_indicator_result_value(orm.Model):

    _name = 'program.result.indicator.value'
    _description = 'Result Indicator Value'
    _columns = {
        'name': fields.date('Date', required=True),
        'value': fields.float('Value', required=True, digits=(1, 2)),
        'uid': fields.many2one('res.users', 'Author', required=True),
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('validated', 'Validated'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ],
            'Status', select=True, required=True, readonly=True,
        ),
        'indicator_id': fields.many2one(
            'program.result.indicator', 'Indicator', required=True,
        ),
    }
    _defaults = {
        'name': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'uid': lambda self, cr, uid, *a: uid,
        'state': 'draft',
    }
    _order = "name desc, create_date desc"
