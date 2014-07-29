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


class program_result_level(orm.Model):

    _name = 'program.result.level'
    _description = 'Result Level'
    _parent_name = 'parent_id'

    def name_get(self, cr, uid, ids, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        return [(line.id, (line.code and line.code + ' - ' or '') + line.name)
                for line in self.browse(cr, uid, ids, context=context)]

    def _get_depth(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        if type(ids) is not list:
            ids = [ids]
        return {
            level.id: (
                self._get_depth(
                    cr, uid, level.parent_id.id, context=context
                )[level.parent_id.id] if level.parent_id else 0) + 1
            for level in self.browse(cr, uid, ids, context=context)
        }

    _columns = {
        'name': fields.char(
            'Name', size=128, required=True, select=True, translate=True),
        'result_ids': fields.one2many(
            'program.result', 'result_level_id', string='Result'),
        'code': fields.char('Code', size=32, translate=True),
        'parent_id': fields.many2one('program.result.level', 'Parent'),
        'child_id': fields.one2many(
            'program.result.level', fields_id='parent_id', string='Child',
            limit=1
        ),
        'depth': fields.function(
            _get_depth, type='integer', string='Level', store=True
        ),
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return _('Error! You can not create recursive Levels.')

    _constraints = [
        (orm.Model._check_recursion, _rec_message, ['parent_id']),
    ]
