# -*- encoding: utf-8 -*-
############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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
############################################################################

{
    'name': 'Program Indicator',
    'version': '1.10',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Customer Relationship Management',
    'summary': 'Program Indicator',
    'description': """
Program Indicator
=================

Contributors
------------
* David Cormier (david.cormier@savoirfairelinux.com)
* Sandy Carter (sandy.carter@savoirfairelinux.com)

""",
    'depends': [
        'program',
    ],
    'license': 'AGPL-3',
    'external_dependencies': {},
    'data': [
        'security/program_indicator_security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'program_result_indicator_view.xml',
        'program_result_indicator_value_view.xml',
        'program_indicator_value_workflow.xml',
        'program_result_view.xml',
        'program_result_level_view.xml',
    ],
    'demo': [
    ],
    'test': [],
    'installable': True,
}
