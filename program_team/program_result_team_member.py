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


class program_result_team_member(orm.Model):

    _name = 'program.result.team.member'
    _description = "Team Member"
    _columns = {
        'result_id': fields.many2one(
            'program.result', string='Result', required=True,
        ),
        'employee_id': fields.many2one(
            'hr.employee', string='Employee', required=True,
        ),
        'role_id': fields.many2one('program.result.team.role', string='Role'),
    }

    def action_member_form_view(self, cr, uid, ids, context=None):
        """Pop-up employee form view for program.result.team.member."""
        if ids and type(ids) is list:
            member_id = ids[0]
        elif type(ids) in (long, int):
            member_id = ids
        else:
            return {}
        member = self.browse(cr, uid, member_id, context=context)
        return {
            'name': member.employee_id.name_get()[0][1],
            'res_model': 'hr.employee',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': member.employee_id.id,
            'context': context,
            'flags': {'form': {'action_buttons': True}},
        }
