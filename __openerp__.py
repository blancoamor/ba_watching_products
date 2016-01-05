# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'watching products',
    'version': '0.1',
    'category': 'blancoamor',
    'description': """
Productos seguidos
======================
Permite generar codigos para estanterias de productos por equipo de ventas.

    """,
    'author': 'Filoquin',
    'website': 'http://sipecu.com.ar',
    'depends': ['base','product','report'],
    'data': [
        'watching_product_label_view.xml',
        'watching_products.xml',
        'report/label.xml',
    ],
    "images":['logo/b.png',],


    'auto_install': False,
}
