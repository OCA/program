# -*- encoding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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

from openerp.osv import orm


class program_result(orm.Model):
    _inherit = 'program.result'

    def _get_documents(self, cr, uid, ids, field_name, args, context=None):
        if not isinstance(ids, list):
            ids = [ids]

        res = super(program_result, self)._get_documents(
            cr, uid, ids, field_name, args, context=context
        )

        ir_attachment_obj = self.pool.get('ir.attachment')

        for line in self.browse(cr, uid, ids, context=context):
            query = [
                '&',
                ('attachment_document_ids.res_model', '=', 'program.evaluation'),
                ('attachment_document_ids.res_id', 'in',
                 [i.id for i in line.evaluation_ids]),
            ]
            res[line.id] += ir_attachment_obj.search(
                cr, uid, query, context=context)

        return res
