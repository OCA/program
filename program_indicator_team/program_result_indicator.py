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
from openerp.addons.program_team.program_result import (
    _department_rule,
    _department_rule_search,
)


class program_indicator_result(orm.Model):

    _inherit = 'program.result.indicator'
    _columns = {
        'department_id': fields.related(
            'result_id',
            'department_id',
            type='many2one',
            relation='hr.department',
            string='Department',
        ),
        'department_rule': fields.function(
            _department_rule,
            fnct_search=_department_rule_search,
            type='boolean',
            method=True,
            string="Department Rule",
        ),
    }
