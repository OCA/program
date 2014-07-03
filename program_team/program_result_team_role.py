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


class program_result_team_role(orm.Model):

    _name = 'program.result.team.role'
    _columns = {
        'name': fields.char('Name', required=True, select=True),
        'is_employee': fields.boolean('Employee'),
        'is_department': fields.boolean('Department'),
        'is_partner': fields.boolean('Partner'),
    }
    _defaults = {
        'is_employee': True,
        'is_department': True,
        'is_partner': True,
    }
