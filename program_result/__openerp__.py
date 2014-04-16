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
    'name': 'Program Result',
    'version': '0.2',
    'category': 'Program',
    'summary': 'RBM Results',
    'description': '''
Program Result
==============

Results Based Management, the Result part thereof.

Contributors
------------

* Alexandre Boily (alexandre.boily@savoirfairelinux.com)
''',
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'depends': [
        'program',
    ],
    'data': [
        'security/ir.model.access.csv',
        'program_action_view.xml',
        'program_result_level_view.xml',
        'program_result_view.xml',
    ],
    'test': [],
    'demo': [
        'program_result_level_demo.xml',
        'program_result_demo.xml',
        'program_action_demo.xml',
    ],
    'auto_install': False,
    'installable': True,
}
