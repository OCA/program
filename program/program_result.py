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

import re
from lxml import etree

from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp import netsvc
import simplejson

from . import _get_validatable

# Be careful when changing the order,
# see program_result_level.default_validation_spec_ids()
STATES = [
    ('draft', _('Draft')),
    ('validated', _('Validated')),
    ('visa_director', _("Director's Visa")),
    ('visa_dpe', _("DPE's Visa")),
    ('visa_admin', _("Admin's Visa")),
    ('opened', _('Opened')),
    ('closed', _('Closed')),
    ('cancel', _('Cancelled')),
]


class program_result(orm.Model):

    _name = 'program.result'
    _description = 'Result'
    _inherit = ['mail.thread']
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
        string = _('%s contributes to')
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

    def _clear_transversal(self, cr, user, ids, context=None):
        """Transverse all children and remove their transversal relations"""
        for result in self.browse(cr, user, ids, context=context):
            child_ids = [child.id for child in result.child_ids]
            self._clear_transversal(cr, user, child_ids, context=context)
            result.write({
                'transverse_child_ids': [(6, False, [])],
                'transverse_parent_ids': [(6, False, [])],
            })

    def _result_level_id(
            self, cr, user, ids=False, parent_id=False, context=None):
        if parent_id:
            parent = self.browse(cr, user, parent_id, context=context)
            parent_level = parent.result_level_id
            if parent_level.child_id:
                return parent_level.child_id[0].id
        else:
            depth = 1
            level_pool = self.pool['program.result.level']
            root_ids = level_pool.search(
                cr, user, [('depth', '=', depth)], context=context
            )
            if root_ids:
                return root_ids[0]
        return False

    def onchange_parent_id(self, cr, user, ids, parent_id, context=None):
        return {
            'value': {
                'result_level_id': self._result_level_id(
                    cr, user, parent_id=parent_id, context=context
                ),
            }
        }

    def create(self, cr, user, vals, context=None):
        if context is None:
            context = {}
        parent_id = vals.get('parent_id')
        level_id = (
            context.get('default_result_level_id') or
            vals.get('result_level_id')
        )
        if not level_id and (parent_id or parent_id is False):
            vals['result_level_id'] = self._result_level_id(
                cr, user, parent_id=parent_id, context=context
            )
        return super(program_result, self).create(
            cr, user, vals, context=context)

    def write(self, cr, user, ids, vals, context=None):
        """Clear transversals if tree structure has changed"""
        parent_id = vals.get('parent_id')
        if parent_id or parent_id is False:
            vals['result_level_id'] = self._result_level_id(
                cr, user, parent_id=parent_id, context=context
            )
            if parent_id is False:
                vals['parent_depth'] = 0
            elif parent_id:
                vals['parent_depth'] = self.read(
                    cr, user, parent_id, ['depth'], context=context
                )['depth']
        res = super(program_result, self).write(
            cr, user, ids, vals, context=context
        )

        if 'parent_id' in vals and not context.get('install_mode'):
            self._clear_transversal(cr, user, ids, context=context)

        return res

    def mass_validate(self, cr, user, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for i in ids:
            wf_service.trg_validate(
                user, self._name, i, 'signal_mass_validate', cr
            )

    def mass_close(self, cr, user, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for i in ids:
            wf_service.trg_validate(
                user, self._name, i, 'signal_mass_close', cr
            )

    def fields_view_get(
            self, cr, user, view_id=None, view_type='form', context=None,
            toolbar=False, submenu=False):
        """Change the readonly fields depending on the groups
        and the settings of the levels

        Non-employees cannot edit the form except for changing the state

        Hide intervention_id in all but last level results
        Hide pages and fields according to the config parameters of
        the level
        """
        def hide_elem(elem, invisible="true"):
            """Set field element's invisibility status

            :param lxml.etree.Element elem: View's field
            :param bool invisible: what to set the invisibility status of field
            """
            modifiers = simplejson.loads(elem.attrib.get('modifiers', "{}"))
            modifiers['invisible'] = invisible
            elem.attrib['modifiers'] = simplejson.dumps(modifiers)

        def ro_elem(elem, readonly="true"):
            """Set field element's read-only status

            :param lxml.etree.Element elem: View's field
            :param bool readonly: what to set the read-only status of field
            """
            modifiers = simplejson.loads(elem.attrib.get('modifiers', "{}"))
            modifiers['readonly'] = readonly
            elem.attrib['modifiers'] = simplejson.dumps(modifiers)

        res = super(program_result, self).fields_view_get(
            cr, user, view_id, view_type, context, toolbar, submenu
        )

        if view_type == 'form':
            level_pool = self.pool['program.result.level']

            arch = etree.fromstring(res['arch'])

            # Change the readonly fields depending on the groups
            has_group = self.pool['res.users'].has_group
            if not has_group(cr, user, 'program.group_program_employee'):
                map(ro_elem, arch.xpath("//field[@name!='state']"))

            # Hide intervention_id from all but last level of results
            lower_level = self.pool['program.result.level'].search(
                cr, user, [], order='depth desc', limit=1, context=context
            )
            parent_depth = context.get('default_parent_depth')
            if lower_level and lower_level[0] - 1 != parent_depth:
                map(hide_elem, arch.xpath("//field[@name='intervention_id']"))

            # Hide pages according to level specification
            for column in level_pool._columns:
                m = re.match('^fvg_show_([^_]*)_([^_]*(_id)?)', column)
                if not m:
                    continue
                xpath = "//%s[@name='%s']" % (m.group(1), m.group(2))
                hidden_levels = level_pool.search(
                    cr, user, [(column, '=', False)], context=context
                )
                for elem in arch.xpath(xpath):
                    hide_elem(elem, [('result_level_id', 'in', hidden_levels)])

            spec_pool = self.pool['program.result.validation.spec']
            states = spec_pool.get_all_states(cr, user, context=context)
            for state in set(states):
                matches = arch.xpath(
                    "//button[@states='%s' and @type='workflow']" % state
                )
                for button in matches:
                    modifiers = simplejson.loads(
                        button.attrib.get('modifiers', "{}")
                    )
                    invisible = modifiers.get('invisible', [])
                    if invisible is True:
                        continue
                    if invisible:
                        invisible.insert(0, '|')
                    invisible.insert(1, ('validation_domain', '!=', True))
                    if invisible:
                        modifiers['invisible'] = invisible
                    button.attrib['modifiers'] = simplejson.dumps(modifiers)

            res['arch'] = etree.tostring(arch)
        return res

    def name_get(self, cr, user, ids, context=None):
        """Format name as code-name or one or the other if the
        other doesn't exist
        """
        name_fields = ['code', 'name']
        if isinstance(ids, (int, long)):
            ids = [ids]
        return [
            (r['id'], '-'.join(filter(None, (r[f] for f in name_fields))))
            for r in self.read(cr, user, ids, name_fields, context=context)
        ]

    def onchange_parent_depth(self, cr, user, ids, parent_depth, context=None):
        res = {}
        if parent_depth == -1:
            res['domain'] = {'parent_id': []}
        return res

    def _get_status(self, cr, uid, context=None):
        """Get statuses from level, technical name needs to be
        untranslated, so context={} in that case.
        The number of elements are truncated to the smallest list
        using zip.
        """
        res = []
        level_id = context.get('default_result_level_id')
        if level_id:
            level_pool = self.pool['program.result.level']
            status_options_no_lang = level_pool.read(
                cr, uid, level_id, ['status_options'], context={}
            )['status_options']
            status_options = level_pool.read(
                cr, uid, level_id, ['status_options'], context=context
            )['status_options']
            if status_options_no_lang and status_options:
                res = [
                    (i.lower().strip(), j.strip())
                    for i, j in zip(status_options_no_lang.split(','),
                                    status_options.split(','))
                ]
        return res

    _columns = {
        'name': fields.char(
            'Name', required=True, select=True, translate=True,
            track_visibility='onchange',
        ),
        'state': fields.selection(
            STATES,
            'State',
            select=True,
            required=True,
            readonly=True,
            track_visibility='onchange',
        ),
        'status_label': fields.related(
            'result_level_id',
            'status_label',
            string='Label for Status',
            type='char',
            readonly=True,
        ),
        'status': fields.selection(
            lambda self, *a, **kw: self._get_status(*a, **kw),
            string='Status of Result',
            select=True,
            track_visibility='onchange',
        ),
        'statement': fields.char(
            'Title', translate=True, track_visibility='onchange',
        ),
        'parent_id': fields.many2one(
            'program.result',
            string='Parent',
            select=True,
            track_visibility='onchange',
            domain="[('id', '!=', id), "
                   "('depth', '=', parent_depth or parent_id.depth)]",
        ),
        'parent_id2': fields.function(
            _get_parent_id, type='many2one', relation='program.result',
            string='Parent', readonly=True),
        'parent_depth': fields.integer('Parent Depth'),
        'child_ids': fields.one2many(
            'program.result', 'parent_id', string='Child Results',
            track_visibility='onchange',
        ),
        'descendant_ids': fields.function(
            _get_descendants, type='one2many', relation='program.result',
            string='Descendant', readonly=True),
        'transverse_child_ids_label': fields.function(
            _transverse_label, type='char', string='Contributes to Label'),
        'transverse_child_ids': fields.many2many(
            'program.result', 'transverse_rel', 'from_id', 'to_id',
            string='Contributes to', track_visibility='onchange',
        ),
        'transverse_parent_ids_label': fields.function(
            _transverse_inv_label, type='char',
            string='Contributed by label'),
        'transverse_parent_ids': fields.many2many(
            'program.result', 'transverse_rel', 'to_id', 'from_id',
            string='Contributed by', track_visibility='onchange',
        ),
        'code': fields.char('Code', size=32, track_visibility='onchange'),
        'result_level_id': fields.many2one(
            'program.result.level', string='Level', select=True,
            track_visibility='onchange', required=True,
        ),
        'depth': fields.related(
            'result_level_id', 'depth', type="integer", string='Depth',
        ),
        'date_from': fields.date('Start Date', track_visibility='onchange'),
        'date_to': fields.date('End Date', track_visibility='onchange'),
        'description': fields.text('Description', translate=True),
        'assumptions': fields.text('Typology of Assumptions', translate=True),
        'risks': fields.text('Typology of Risks', translate=True),
        'target_audience_type_ids': fields.many2many(
            'program.result.target', string='Target Audience Types'
        ),
        'intervention_id': fields.many2one(
            'program.result.intervention', string='Intervention Mode'
        ),
        'tag_ids': fields.many2many('program.result.tag', string='Tags'),
        'validation_domain': fields.function(
            lambda *a, **kw: _get_validatable(*a, **kw),
            type='boolean',
            string="Validation Domain Search",
        ),
    }
    _defaults = {
        'state': 'draft',
        'status_label': lambda self, cr, uid, context: _('Status'),
        'transverse_child_ids_label': (
            lambda self, cr, uid, context:
            self._transverse_label(cr, uid, context=context)
        ),
        'transverse_parent_ids_label': (
            lambda self, cr, uid, context:
            self._transverse_inv_label(cr, uid, context=context)
        ),
        'result_level_id': (
            lambda self, cr, uid, context:
            self._result_level_id(cr, uid, context=context)
        ),
        'parent_depth': -1,
    }

    def _rec_message(self, cr, uid, ids, context=None):
        return "\n\n" + _('Error! You can not create recursive Results.')

    _constraints = [
        (orm.Model._check_recursion, _rec_message, ['parent_id']),
    ]
