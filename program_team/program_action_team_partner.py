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


class program_action_team_partner(orm.Model):

    _name = 'program.action.team.partner'

    _columns = {
        'action': fields.many2one(
            'program.action',
            string='Action',
        ),

        'organisation': fields.many2one(
            'res.partner',
            string='Organisation',
            required=True,
        ),

        'role': fields.many2one(
            'program.action.team.role',
            string='Role',
        ),

        'contribution': fields.text(
            'Non-Financial Contribution',
            help=(
                'Arbitrary contribution, usually a non-financial or ' +
                'unquantifiable one.'
            ),
        ),
    }
