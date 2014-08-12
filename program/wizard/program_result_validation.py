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
from openerp.tools.translate import _

from ..program_result import STATES


class program_result_validation(orm.TransientModel):
    """Form to mass-validate results based on their
    states and user's group rights
    """

    _name = 'program.result.validation'
    _description = "Result Mass Validator"
    _columns = {
        'line_ids': fields.many2many(
            'program.result.validation.line',
            'program_result_validation_rel',
            string='Results',
        ),
    }

    def _build_result_ids(self, cr, uid, context=None):
        if context is None:
            context = {}
        res = []
        result_line_pool = self.pool['program.result.validation.line']
        for result_id in context.get('active_ids', []):
            res.append(result_line_pool.create(
                cr, uid, {
                    'result_id': result_id,
                }, context=context
            ))
        return res

    _defaults = {
        'line_ids': _build_result_ids,
    }

    def run(self, cr, uid, ids, context=None):
        if type(ids) is list and ids:
            ids = ids[0]
        result_ids = []
        unvalidatable_ids = []
        for line in self.browse(cr, uid, ids, context=context).line_ids:
            if line.is_validatable:
                result_ids.append(line.result_id)
            else:
                unvalidatable_ids.append(line.result_id)
        if unvalidatable_ids:
            # Don't do the following in a generator as it doesn't translate
            culprits = set()
            for r in unvalidatable_ids:
                culprits.add((r.name, _(dict(STATES)[r.state])))
            raise orm.except_orm(
                _('Error'),
                _("The following results cannot be validated or "
                  "you don't have the required permissions:\n\n%s") % (
                      '\n'.join("%s (%s)" % c for c in culprits))
            )
        for result in result_ids:
            result.mass_validate()
        return {}
