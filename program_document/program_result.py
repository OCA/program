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
    """Model Program Document"""

    _description = __doc__
    _inherit = 'program.result'

    def _get_documents(self, cr, uid, ids, field_name, args, context=None):
        res = {}

        if not isinstance(ids, list):
            ids = [ids]

        ir_attachment_obj = self.pool.get('ir.attachment')

        for line in self.browse(cr, uid, ids, context=context):
            query = [
                '|',
                '&', ('attachment_document_ids.res_model', '=', 'program.result'),
                ('attachment_document_ids.res_id', '=', line.id),
                '&', ('attachment_document_ids.res_model', '=', 'program.evaluation'),
                ('attachment_document_ids.res_id', 'in', [i.id for i in line.evaluation]),
            ]
            res[line.id] = ir_attachment_obj.search(
                cr, uid, query, context=context)

        return res

    _columns = {
        'document_ids': fields.function(
            _get_documents,
            type='many2many',
            obj='ir.attachment',
            string='Documents')
    }
