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


class program_action_team_role(orm.Model):

    _name = 'program.action.team.role'

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
        ),

        'employee': fields.boolean(
            'Employee',
        ),

        'department': fields.boolean(
            'Department',
        ),

        'partner': fields.boolean(
            'Partner',
        ),
    }

    _defaults = {
        'employee': True,
        'department': True,
        'partner': True,
    }
