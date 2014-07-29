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


class program_indicator_result(orm.Model):

    _name = 'program.result.indicator'
    _columns = {
        'name': fields.char('Name'),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('open', 'Open'),
            ('submitted', 'Submitted'),
            ('validated', 'Validated'),
            ('cancel', 'Cancelled'),
        ], 'Status', select=True, required=True, readonly=True),
        'result_id': fields.many2one(
            'program.result', 'Result', required=True
        ),
        'value_initial': fields.char('Initial Value'),
        'value_target': fields.char('Target Value'),
        'value': fields.char('Value'),
        'value_date': fields.datetime('Date'),
        'partner_id': fields.many2one('res.partner', 'Manager of follow-up'),
        'comment': fields.text('Comment'),
    }
    _defaults = {
        'state': 'draft',
    }
