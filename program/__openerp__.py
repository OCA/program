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

{
    'name': 'Program',
    'version': '7.0.1.10.1',
    'category': 'Program',
    'summary': 'Results Based Management',
    'description': '''
Program
=======

Results Based Management

Contributors
------------

* Alexandre Boily (alexandre.boily@savoirfairelinux.com)
* Sandy Carter (sandy.carter@savoirfairelinux.com)
''',
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'mail',
    ],
    'data': [
        'security/program_security.xml',
        'security/ir.model.access.csv',
        'wizard/program_result_validation.xml',
        'wizard/program_result_close.xml',
        'program_result_view.xml',
        'program_result_level_view.xml',
        'program_result_target_view.xml',
        'program_result_intervention_view.xml',
        'program_result_tag_view.xml',
        'program_result_workflow.xml',
    ],
    'test': [],
    'demo': [
        'program_result_level_demo.xml',
        'program_result_demo.xml',
    ],
    'auto_install': False,
    'installable': True,
}
