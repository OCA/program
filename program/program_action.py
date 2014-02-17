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


class program_action(orm.Model):

    _name = 'program.action'
    _parent_name = 'parent'

    _columns = {
        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
        ),

        'parent': fields.many2one(
            'program.action',
            string='Parent',
            select=True,
        ),

        'children': fields.one2many(
            'program.action',
            'parent',
            string='Sub-actions',
        ),

        'transverse': fields.many2many(
            'program.action',
            'transverse_rel',
            'from_id',
            'to_id',
            string='Transverse',
        ),

        'code': fields.char(
            'Code',
            size=32,
        ),

        'level': fields.many2one(
            'program.action.level',
            string='Level',
            required=True,
            select=True,
        ),

        'date_from': fields.date(
            'Start Date',
        ),

        'date_to': fields.date(
            'End Date',
        ),

        'description': fields.text(
            'Description',
        ),

        'target_audience': fields.text(
            'Target Audience',
        ),

        'target_audience_type': fields.many2many(
            'program.action.target',
            'action_target_rel',
            'action_id',
            'target_id',
            string='Target Audience Types',
        ),
    }
