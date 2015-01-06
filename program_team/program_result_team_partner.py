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


class program_result_team_partner(orm.Model):

    def _rec_message(self, cr, uid, ids, context=None):
        return _('This partner is already part of the partner list.')

    _name = 'program.result.team.partner'
    _description = "Team Partner"
    _columns = {
        'result_id': fields.many2one('program.result', string='Result'),
        'partner_id': fields.many2one(
            'res.partner',
            string='Partner',
            required=True,
        ),
        'country_id': fields.related(
            'partner_id',
            'country_id',
            type='many2one',
            relation='res.country',
            string='Country',
            readonly=True,
        ),
        'type_id': fields.many2many(
            'program.result.team.partner.type',
            "program_result_team_partner_type_rel",
            id1='partner_id',
            id2='type_id',
            string="Category"
        ),
    }
    _sql_constraints = [
        ('unique_partner', 'UNIQUE(result_id, partner_id)', _rec_message),
    ]

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
