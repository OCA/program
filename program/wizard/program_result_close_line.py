# -*- encoding: utf-8 -*-
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

from openerp.osv import orm, fields

from ..program_result import STATES


class program_result_close_line(orm.TransientModel):
    """Form to mass-close results based on their
    states and user's group rights
    """

    _name = 'program.result.close.line'
    _description = "Result Mass Closer Line"

    def _get_mapping(self):
        """
        * program.group_program_dpe: close
        """
        return [
            ('program.group_program_dpe', ['opened']),
        ]

    def _get_closable(self, cr, uid, ids, name, args, context=None):
        """Check the user's rights to change states based on
        group and view_program_result_form's buttons
        """
        users_pool = self.pool['res.users']
        res = {i: False for i in ids}
        for group, states in self._get_mapping():
            if users_pool.has_group(cr, uid, group):
                res.update({i: True for i in self.search(
                    cr, uid, [
                        ('id', 'in', ids),
                        ('state', 'in', states),
                    ], context=context)
                })
        return res

    _columns = {
        'is_closable': fields.function(
            lambda self, *a, **kw: self._get_closable(*a, **kw),
            string='Can be Validated',
            type='boolean',
        ),
        'result_id': fields.many2one(
            'program.result',
            string='Results',
        ),
        'name': fields.related(
            'result_id',
            'name',
            string='Name',
            type='char',
        ),
        'state': fields.related(
            'result_id',
            'state',
            string='State',
            type='selection',
            selection=STATES,
        ),
    }
