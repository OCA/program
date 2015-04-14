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


class program_result_level(orm.Model):
    _inherit = 'program.result.level'
    _columns = {
        'fvg_show_page_indicators': fields.boolean('Show "Indicator" Tab'),
    }
    _defaults = {
        'fvg_show_page_indicators': True,
    }

    def default_validation_spec_ids(self, cr, uid, context=None):
        """Add validation entry for coordinator at "validated" state
        """
        coordinator = self.pool['ir.model.data'].get_object(
            cr, uid, "program_indicator", "group_program_coordinator"
        )
        states = [
            "validated",
        ]
        res = super(program_result_level, self).default_validation_spec_ids(
            cr, uid, context=context
        )
        res.append((0, 0, {
            'group_id': coordinator.id,
            'states': ','.join(states)
        }))
        return res
