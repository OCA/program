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
    'name': 'Program Evaluation - Team',
    'version': '1.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'category': 'Customer Relationship Management',
    'license': 'AGPL-3',
    'summary': 'Program Evaluation',
    'description': """
Program Evaluation - Team bindings
==================================

Add department to recommendation

Contributors
-------------
* Sandy Carter (sandy.carter@savoirfairelinux.com)
""",
    'depends': [
        'program_evaluation',
        'program_team',
    ],
    'data': [
        'program_recommendation_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
