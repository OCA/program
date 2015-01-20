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


class program_result(orm.Model):

    _inherit = 'program.result'
    _columns = {
        'top_level_menu_id': fields.function(
            lambda self, *a, **kw: self._get_top_level_menu_id(*a, **kw),
            fnct_search=(
                lambda self, *a, **kw: self._search_top_level_menu_id(*a, **kw)
            ),
            type="many2one",
            relation='ir.ui.menu',
            string='Top Level Menu',
        ),
    }

    def _get_top_level_menu_id(self, cr, uid, ids, name=None, args=None,
                               context=None):
        return {
            r.id: r.result_level_id.chain_root.top_level_menu_id.id
            for r in self.browse(cr, uid, ids, context=context)
        }

    def _search_top_level_menu_id(self, cr, uid, model, name=None, args=None,
                                  context=None):
        res = []
        level_id = context.get('default_result_level_id')
        if args and len(args[0]) == 3 and args[0][2] is not False:
            args[0] = (
                'result_level_id.chain_root.%s' % name, args[0][1], args[0][2]
            )
            res += args
        elif level_id:
            res.append(
                (
                    'result_level_id.chain_root.%s' % name,
                    '=', self.pool['program.result.level'].browse(
                        cr, uid, level_id, context=context
                    ).chain_root.top_level_menu_id.id
                )
            )
        return res
