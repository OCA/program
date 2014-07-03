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


class program_result_team_partner(orm.Model):

    _name = 'program.result.team.partner'

    _columns = {
        'result_id': fields.many2one('program.result', string='Result'),
        'organisation_id': fields.many2one(
            'res.partner', string='Organisation', required=True,
        ),
        'role_id': fields.many2one('program.result.team.role', string='Role'),
        'type_id': fields.many2one(
            'program.result.team.partner.type', string="Type"
        ),
        'contribution': fields.text(
            'Non-Financial Contribution',
            help=(
                'Arbitrary contribution, usually a non-financial or '
                'unquantifiable one.'
            ),
        ),
    }

    def action_partner_form_view(self, cr, uid, ids, context=None):
        """Pop-up partner form view for program.result.team.partner."""
        if ids and type(ids) is list:
            partner_id = ids[0]
        elif type(ids) in (long, int):
            partner_id = ids
        else:
            return {}
        partner = self.browse(cr, uid, partner_id, context=context)
        model_data_pool = self.pool['ir.model.data']
        return {
            'name': partner.organisation_id.name_get()[0][1],
            'res_model': 'res.partner',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': partner.organisation_id.id,
            'context': context,
            'view_id': model_data_pool.get_object_reference(
                cr, uid, 'program_team', 'view_partner_form')[1]
        }

