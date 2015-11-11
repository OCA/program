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

from openerp.osv import orm
from openerp.tools.translate import _


class account_analytic_account(orm.Model):

    _inherit = 'account.analytic.account'

    def _get_propagatable_fields(self):
        return {
            'name',
            'code',
        }

    def _get_related_result(self, cr, uid, account_id, context=None):
        """ Return the parent result analytic id."""

        if not account_id:
            return False
        else:
            result_pool = self.pool.get('program.result')

            parent_result_id = result_pool.search(cr, uid, [
                ('account_analytic_id', '=', account_id)
            ], context=context)

            if not parent_result_id:
                return False

            return result_pool.browse(
                cr, uid, parent_result_id[0], context=context)

    def create(self, cr, uid, vals, context=None):
        """ Create an analytic account

        Create the related result if this account is under
        the root program node"""
        context = {} if context is None else context

        account_id = super(account_analytic_account, self).create(
            cr, uid, vals, context=context
        )

        if context.get('result_written', False):
            return account_id

        parent_id = vals.get('parent_id', False)

        # If there is no parent ID it cannot be under the root
        # program node.
        if not parent_id:
            return account_id

        # If the parent analytic account is related has an associated
        # result, we assume we are under the root program node.
        parent_result = self._get_related_result(cr, uid, parent_id,
                                                 context=context)

        # If there are NO parent results we don't need to create the related
        # result
        if not parent_result:
            return account_id

        result_pool = self.pool.get('program.result')

        if parent_result:
            parent_result_id = parent_result.id
        else:
            parent_result_id = False

        propagated_fields = {
            i: j
            for i, j in vals.items() if i in self._get_propagatable_fields()
        }

        result_pool.create(
            cr, uid, dict(propagated_fields.items() + {
                'name': vals.get('name', False),
                'code': vals.get('code', False),
                'account_analytic_id': account_id,
                'parent_id': parent_result_id,
            }.items()),
            context=dict(context, account_written=True)
        )
        return account_id

    def write(self, cr, uid, ids, values, context=None):

        result_pool = self.pool.get('program.result')

        if context is None:
            context = {}

        if type(ids) not in (list, ):
            ids = [ids]

        res = super(account_analytic_account, self).write(
            cr, uid, ids, values, context=context
        )

        if context.get('result_written', False):
            return res

        for account in self.browse(cr, uid, ids, context=context):
            propagated_fields = {
                i: j for i, j in values.items()
                if i in self._get_propagatable_fields()
            }

            if values.get('parent_id'):
                propagated_fields['parent_id'] = False

                related_result = self._get_related_result(
                    cr, uid, values['parent_id'], context=context
                )

                if related_result:
                    propagated_fields['parent_id'] = related_result.id

            if propagated_fields:
                related_result = result_pool.search(
                    cr, uid,
                    [('account_analytic_id', '=', account.id), ],
                    context=context
                )

                result_pool.write(
                    cr, uid, related_result, propagated_fields,
                    context=dict(context, account_written=True)
                )

        return res

    def unlink(self, cr, uid, ids, context=None):
        result_pool = self.pool.get('program.result')
        if type(ids) is not list:
            ids = [ids]
        if result_pool.search(cr, uid, [('account_analytic_id', 'in', ids)],
                              context=context):
            raise orm.except_orm(
                _('Error'),
                _('Account still associated with a Program Result'))
        return super(account_analytic_account, self).unlink(
            cr, uid, ids, context=context
        )
