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

import re

from openerp.osv import fields, orm


RE_GROUP_FROM = [
    re.compile(r"\[\('state', '!=', 'draft'\)\]"),
    re.compile(
        r"\[\[&quot;state&quot;, &quot;!=&quot;, &quot;draft&quot;\]\]"
    ),
]
RE_GROUP_TO = [
    "[('state', 'not in', ('draft', 'validated'))]",
    "[[&quot;state&quot;, &quot;not in&quot;, "
    "[&quot;draft&quot;, &quot;validated&quot;]]]",
]


class program_result(orm.Model):

    _inherit = 'program.result'

    _columns = {
        'result_indicator_ids': fields.one2many(
            'program.result.indicator', 'result_id', 'Result Indicator',
        ),
    }

    def fields_view_get(
            self, cr, user, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        """Give access to Coordinator for write in validated of fields which
        are normally not editable by other groups.

        This allows this user to do corrections after validation.

        Look for the strings "[('state', '!=', 'draft')]"
        exactly in the xml view and replace it with
        "[('state', 'not in', ('draft', 'validated'))]"
        """

        res = super(program_result, self).fields_view_get(
            cr, user, view_id, view_type, context, toolbar, submenu
        )

        if view_type == 'form':
            user_pool = self.pool['res.users']
            # Change the readonly fields depending on the groups
            if user_pool.has_group(
                    cr, user, 'program_indicator.group_program_coordinator'):
                for FROM, TO in zip(RE_GROUP_FROM, RE_GROUP_TO):
                    res['arch'] = FROM.sub(TO, res['arch'])
        return res
