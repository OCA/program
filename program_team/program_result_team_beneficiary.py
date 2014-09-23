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


class program_result_team_beneficiary(orm.Model):

    def _rec_message(self, cr, uid, ids, context=None):
        return _('This partner is already part of the beneficiary list.')

    _name = 'program.result.team.beneficiary'
    _description = "Team Beneficiary"
    _columns = {
        'result_id': fields.many2one('program.result', string='Result'),
        'partner_id': fields.many2one(
            'res.partner',
            string='Beneficiary',
            required=True,
            domain=[('is_company', '=', 'True')],
        ),
        'country_id': fields.related(
            'partner_id',
            'country_id',
            type='many2one',
            relation='res.country',
            string='Country',
            readonly=True,
        ),
        'type_id': fields.many2one(
            'program.result.team.beneficiary.type',
            string="Type"
        ),
    }
    _sql_constraints = [
        ('unique_partner', 'UNIQUE(result_id, partner_id)', _rec_message),
    ]
