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
    _description = 'Result Indicator'

    def _current_value(self, cr, uid, ids, name, arg, context=None):
        """Get most recent suggested value are return related value"""
        if context is None:
            context = {}
        res = {}
        if name == 'value':
            field = 'value'
        elif name == 'value_uid':
            field = 'uid'
        else:
            return res
        value_pool = self.pool['program.result.indicator.value']
        for i in ids:
            value_ids = value_pool.search(
                cr, uid, [
                    ('indicator_id', '=', i),
                    ('state', '!=', 'cancel')
                ], limit=1)
            value_read = value_pool.read(
                cr, uid, value_ids, [field], context=context
            )
            # search has not found anything, leave empty
            if not value_read:
                res[i] = False
            else:
                res[i] = value_read[0][field]
        return res

    def _current_value_inv(self, cr, uid, ids, name, val, arg, context=None):
        """Log changes to value as new indicator values"""
        if name != 'value' or not val:
            return
        if type(ids) is not list:
            ids = [ids]
        value_pool = self.pool['program.result.indicator.value']
        for indicator in self.browse(cr, uid, ids, context=context):
            value_id = value_pool.create(cr, uid, {
                'indicator_id': indicator.id,
                'value': val,
            }, context=context)
            indicator.write({'value_logged_ids': [(4, value_id)]})

    _columns = {
        'name': fields.char('Name'),
        'result_id': fields.many2one(
            'program.result', 'Result', required=True
        ),
        'value_initial': fields.char('Initial Value'),
        'value_target': fields.char('Target Value'),
        'value': fields.function(
            _current_value, fnct_inv=_current_value_inv,
            type='char', string='Value',
        ),
        'value_uid': fields.function(
            _current_value, type='many2one', obj='res.users',
            string='Last Modified by',
        ),
        'value_logged_ids': fields.one2many(
            'program.result.indicator.value', 'indicator_id', 'Logged Values'
        ),
        'partner_id': fields.many2one('res.partner', 'Manager of follow-up'),
        'comment': fields.text('Comment'),
    }
