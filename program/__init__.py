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


def _get_mapping_general(self, cr, uid, ids, context=None):
    res = {}
    result_pool = self.pool['program.result']
    for result in result_pool.browse(cr, uid, ids, context=context):
        group_specs = {}
        level_id = result.result_level_id.chain_root
        for validation_spec in level_id.validation_spec_ids:
            states = group_specs.get(validation_spec.group_id.id, set())
            states.update((validation_spec.states or "").split(','))
            group_specs[validation_spec.group_id.id] = states
        res[result.id] = group_specs
    return res


def _get_validatable(self, cr, uid, ids, name=None, args=None, context=None):
    """Check the user's rights to change states based on
    group and view_program_result_form's buttons
    """
    def has_group(cr, uid, gid):
        cr.execute("""
SELECT 1
FROM res_groups_users_rel
WHERE uid=%s AND gid = %s""", (uid, gid))
        return bool(cr.fetchone())
    res = {}
    result_pool = self.pool['program.result']
    if hasattr(self, '_get_mapping'):
        mappings = self._get_mapping(cr, uid, ids, context=context)
    else:
        mappings = _get_mapping_general(self, cr, uid, ids, context)
    for result in result_pool.browse(cr, uid, ids, context=context):
        for gid, states in mappings[result.id].iteritems():
            if has_group(cr, uid, gid) and result.state in states:
                res[result.id] = True
                break
        else:
            res[result.id] = False
    return res


def _get_wizard_validatable(self, cr, uid, ids, name, args, context=None):
    result_ids = {
        line.result_id.id: line.id
        for line in self.browse(cr, uid, ids, context=context)
    }
    res = _get_validatable(self, cr, uid, result_ids.keys(), context=context)
    return {
        line_id: res.get(result_id, {})
        for result_id, line_id in result_ids.iteritems()
    }


from . import (
    program_result,
    program_result_level,
    program_result_target,
    program_result_intervention,
    program_result_tag,
    program_result_validation_spec,
    wizard,
)  # noqa: E402 functions need to be defined before imports so they can be used
