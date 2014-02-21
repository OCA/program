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


class program_recommendation(orm.Model):

    _name = 'program.recommendation'

    _columns = {

        'code': fields.char(
            'Code',
            size=32,
        ),

        'name': fields.char(
            'Name',
            size=128,
            required=True
        ),

        'description': fields.text(
            'Description'
        ),

        'evaluation_id': fields.many2one(
            'program.evaluation',
            'Evaluation'
        )

    }


class program_action(orm.Model):

    _inherit = 'program.action'

    _columns = {
        'evaluation': fields.one2many(
            'program.evaluation',
            'action_id',
            string='Evaluations',
        ),

    }


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
            'Status',
            select=True,
            required=True,
            readonly=True
        ),

        'name': fields.char(
            'Name',
            size=128,
            required=True,
            select=True,
        ),

        'abstract': fields.text(
            'Abstract'
        ),

        'action_id': fields.many2one(
            'program.action',
            'Action',
        ),

        'date_start': fields.date(
            'Start date',
        ),

        'date_end': fields.date(
            'End date',
        ),

        'evaluator_id': fields.many2many(
            'res.partner',
            'evaluators_rel',
            'from_id',
            'to_id',
            string='Evaluator',
        ),

        'recommendation_id': fields.one2many(
            'program.recommendation',
            'evaluation_id',
            'Recommendation',
        ),
    }
