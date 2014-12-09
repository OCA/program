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
from openerp.tools.translate import _


class program_result_country(orm.Model):

    def _rec_message(self, cr, uid, ids, context=None):
        return _('A country and role pair has been entered twice.')

    _name = 'program.result.country'
    _description = "Target Country"
    _columns = {
        'result_id': fields.many2one(
            'program.result',
            string='Result',
            select=True,
            required=True,
        ),
        'name': fields.many2one(
            'res.country',
            string='Name',
            select=True,
            required=True,
        ),
        'code': fields.related(
            'name',
            'code',
            type='char',
            readonly=True,
            string='Code',
            select=True,
        ),
        'role': fields.many2one('program.result.country.role', string='Role'),
    }
    _sql_constraints = [
        ('unique_country_role', 'UNIQUE(result_id, name, role)', _rec_message),
    ]
