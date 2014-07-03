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

    _name = 'program.indicator.result'
    _columns = {
        'state': fields.selection([
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('open', 'Open'),
            ('submitted', 'Submitted'),
            ('validated', 'Validated'),
            ('cancel', 'Cancelled'),
        ], 'Status', select=True, required=True, readonly=True),
        'indicator_id': fields.many2one(
            'program.indicator', 'Indicator', required=True
        ),
        'result_id': fields.many2one(
            'program.result', 'Result', required=True
        ),
        'mandatory': fields.boolean('Mandatory'),
        'verification_means': fields.text('Verification Means'),
        'risk_hypothesis': fields.text('Risk hypothesis'),
        'value_initial': fields.char('Initial Value'),
        'value_target': fields.char('Target Value'),
        'value': fields.char('Value'),
        'value_date': fields.datetime('Date'),
        'partner_id': fields.many2one('res.partner', 'User'),
        'comment': fields.text('Comment'),
    }
    _defaults = {
        'state': 'draft',
    }

    def change_indicator(self, cr, uid, ids, indicator_id, context=None):
        indicator = self.pool.get('program.indicator').browse(
            cr, uid, indicator_id, context=context)

        return {
            'value': {
                'verification_means': indicator.verification_means,
                'risk_hypothesis': indicator.risk_hypothesis
            }
        }
