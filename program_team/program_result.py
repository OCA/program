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


def _department_rule(self, cr, uid, ids, name, args, context=None):
    if isinstance(ids, (int, long)):
        ids = [ids]
    return {i: True for i in ids}


def _department_rule_search(
        self, cr, uid, obj=None, name=None, args=None, context=None):
    user_pool = self.pool['res.users']
    if type(args) is list:
        # uid lies, so get current user from arguments
        user = args[0][2]
    else:
        user = args
    if type(user) is int:
        user = user_pool.browse(cr, uid, user, context=context)
    if user_pool.has_group(cr, user.id, 'program.group_program_dpe'):
        return []
    ids = [
        employee.department_id.id
        for employee in user.employee_ids
        if employee.department_id
    ]
    ids.append(False)
    if self._name != 'hr.department':
        ids = self.search(
            cr, uid, [('department_id', 'in', ids)], context=context
        )
    return [('id', 'in', ids)]


class program_result(orm.Model):

    _inherit = 'program.result'
    _columns = {
        'department_id': fields.many2one(
            'hr.department',
            string="Department",
            select=True
        ),
        'team_department_ids': fields.one2many(
            'program.result.team.department',
            'result_id',
            string='Departments',
        ),
        'team_member_ids': fields.one2many(
            'program.result.team.member',
            'result_id',
            string='Team Members',
        ),
        'team_beneficiary_ids': fields.one2many(
            'program.result.team.beneficiary',
            'result_id',
            string='Beneficiaries',
        ),
        'team_has_partners': fields.boolean('Has Partners'),
        'team_partner_ids': fields.one2many(
            'program.result.team.partner',
            'result_id',
            string='Partners',
        ),
        'department_rule': fields.function(
            _department_rule,
            fnct_search=_department_rule_search,
            type='boolean',
            method=True,
            string="Department Rule",
        ),
    }
    _defaults = {
        'team_has_partners': True,
    }
