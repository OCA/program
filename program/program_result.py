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


class program_result(orm.Model):

    _name = 'program.result'
    _parent_name = 'parent_id'

    def _get_descendants(self, cr, uid, ids, name=None, args=None,
                         context=None):
        """Return any result which is either a child or recursively a child
        of result.
        """
        res = {}
        if context is None:
            context = {}
        if type(ids) is not list:
            ids = [ids]
        for result in self.browse(cr, uid, ids, context=context):
            child_list = [r.id for r in result.child_ids]
            for child in result.child_ids:
                child_list += child._get_descendants(child.id)[child.id]
            res[result.id] = child_list
        return res

    def _get_parent_id(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        return {
            result.id: result.parent_id.id
            for result in self.browse(cr, uid, ids, context=context)
        }

    def _transverse_label(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        string = _('Contributes to %s')
        if ids is None:
            return string % ''
        return {
            result.id: string % result.name or ''
            for result in self.browse(cr, uid, ids, context=context)
        }

    def _transverse_inv_label(
            self, cr, uid, ids=None, name=None, args=None, context=None):
        string = _('Contributed by %s')
        if ids is None:
            return string % ''
        return {
            result.id: string % result.name or ''
            for result in self.browse(cr, uid, ids, context=context)
        }

    _columns = {
        'name': fields.char(
            'Name', required=True, select=True, translate=True),
        'long_name': fields.char('Long name', translate=True),
        'parent_id': fields.many2one(
            'program.result', string='Parent', select=True),
        'parent_id2': fields.function(
            _get_parent_id, type='many2one', relation='program.result',
            string='Parent', readonly=True),
        'child_ids': fields.one2many(
            'program.result', 'parent_id', string='Child Results'),
        'descendant_ids': fields.function(
            _get_descendants, type='one2many', relation='program.result',
            string='Descendant', readonly=True),
        'transverse_label': fields.function(
            _transverse_label, type='char', string='Contributes to Label'),
        'transverse_ids': fields.many2many(
            'program.result', 'transverse_rel', 'from_id', 'to_id',
            string='Contributes to'),
        'transverse_inv_label': fields.function(
            _transverse_inv_label, type='char',
            string='Contributed by label'),
        'transverse_inv_ids': fields.many2many(
            'program.result', 'transverse_rel', 'to_id', 'from_id',
            string='Contributed by'),
        'code': fields.char('Code', size=32),
        'result_level_id': fields.many2one(
            'program.result.level', string='Level', select=True),
        'depth': fields.related(
            'result_level_id', 'depth', type="integer", string='Depth'),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
        'description': fields.text('Description', translate=True),
        'target_audience': fields.text('Target Audience', translate=True),
        'target_audience_type_ids': fields.many2many(
            'program.result.target', string='Target Audience Types'
        ),
    }
    _defaults = {
        'transverse_label': lambda s, c, u, context: s._transverse_label(
            c, u, context=context),
        'transverse_inv_label': lambda s, c, u, cx: s._transverse_inv_label(
            c, u, context=cx),
    }
