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


class program_evaluation(orm.Model):

    _name = 'program.evaluation'
    _defaults = {
        'state': 'draft'
    }
    _columns = {
        'state': fields.selection(
            [
                ('draft', 'Draft'),
                ('plan', 'Planned'),
                ('setup', 'Setup'),
                ('ongoing', 'Ongoing'),
                ('done', 'Done'),
                ('cancel', 'Cancelled'),
            ],
            'Status', select=True, required=True, readonly=True),
        'name': fields.char('Name', size=128, required=True, select=True),
        'abstract': fields.text('Abstract'),
        'result_id': fields.many2one('program.result', 'Result'),
        'date_start': fields.date('Start date'),
        'date_end': fields.date('End date'),
        'evaluator_ids': fields.many2many(
            'res.partner', 'evaluators_rel', 'from_id', 'to_id',
            string='Evaluator'),
        'recommendation_ids': fields.one2many(
            'program.recommendation', 'evaluation_id', 'Recommendation'),
    }
