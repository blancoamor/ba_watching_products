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
import openerp
from openerp import models, fields, api
from openerp.osv import orm, fields, osv

from datetime import date 
#import pdb
import logging
_logger = logging.getLogger(__name__)

class product_product(osv.osv):

    _name = 'product.product'
    _inherit = 'product.product' 

    def ba_price_frendly_style(self,price):
        price_text=str(price).split('.')
        return "$ " + price_text[0] + "<sup>" + price_text[1] + "</sup>"
    def _fnct_pricelist_price(self, cr, uid, ids, field_name, args, context=None):
        product_pricelist_obj = self.pool.get('product.pricelist')

        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            price_pricelist=self.pool.get('product.pricelist').price_get(cr,uid,[2],product.id,1.0,1,{'uom':1,'date':unicode(date.today())})

            res[product.id] = ''
            if 2 in price_pricelist:
                sum_tax = 0
                for tax in product.taxes_id:
                    sum_tax += price_pricelist[2] * tax.amount
                    res[product.id] =str('%.2f' % (price_pricelist[2] + tax.amount) )

        return res


    def _fnct_sales_condition_text(self, cr, uid, ids, field_name, args, context=None):
        product_pricelist_obj = self.pool.get('product.pricelist')
        if context is None:
            context = {}
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            product_pricelist=product_pricelist_obj.browse(cr, uid, 31, context=context)
            res[product.id]="";

            price_pricelist=self.pool.get('product.pricelist').price_get(cr,uid,[31 ],product.id,1.0,1,{'uom':1,'date':unicode(date.today())})
            sum_tax = 0
            for tax in product.taxes_id:
                sum_tax += price_pricelist[31] * tax.amount
                for conditions_id in product_pricelist['pricelist_sale_condition'] :
                    if conditions_id['fee'] == 1 :
                        res[product.id]+=   conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[31] + tax.amount)) + "  | "             
                    else :
                        res[product.id]+= conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[31] + tax.amount) / conditions_id['fee']) + ' (Total: ' +"${0:.2f}".format((price_pricelist[31] + tax.amount))  + ') | ' 

            for pricelist_child in product_pricelist['pricelist_id_set'] :                
                price_pricelist=self.pool.get('product.pricelist').price_get(cr,uid,[pricelist_child['id']],product.id,1.0,1,{'uom':1,'date':unicode(date.today())})
                sum_tax = 0
                for tax in product.taxes_id:
                    sum_tax += price_pricelist[pricelist_child['id']] * tax.amount
                    for conditions_id in pricelist_child['pricelist_sale_condition'] :
                        if conditions_id['fee'] == 1 :
                            res[product.id]+=   conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[pricelist_child['id']] + tax.amount)) + "  | "             
                        else :
                            res[product.id]+= conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[pricelist_child['id']] + tax.amount) / conditions_id['fee']) + ' (Total: ' +"${0:.2f}".format((price_pricelist[pricelist_child['id']] + tax.amount))  + ') | ' 
        return res






    _columns = {
        'total_price': fields.function(_fnct_pricelist_price, string='Precio con impuestos',type='char', size=256,),
        'total_price_condition_text': fields.function(_fnct_sales_condition_text, string='condiciones',type='text',),
    }



