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

    _columns = {
        'name': fields.char(
            'Name', required=True, select=True, translate=True),
        'parent_id': fields.many2one(
            'program.result', string='Parent', select=True),
        'child_ids': fields.one2many(
            'program.result', 'parent_id', string='Child Results'),
        'descendant_ids': fields.function(
            _get_descendants, type='one2many', relation='program.result',
            string='Descendant', readonly=True),
        'is_transversal': fields.boolean('Transversal'),
        'transverse_ids': fields.many2many(
            'program.result', 'transverse_rel', 'from_id', 'to_id',
            string='Transverse'),
        'code': fields.char('Code', size=32),
        'result_level_id': fields.many2one(
            'program.result.level', string='Level', select=True),
        'date_from': fields.date('Start Date'),
        'date_to': fields.date('End Date'),
        'description': fields.text('Description', translate=True),
        'target_audience': fields.text('Target Audience', translate=True),
        'target_audience_type_ids': fields.many2many(
            'program.result.target', string='Target Audience Types'
        ),
    }
