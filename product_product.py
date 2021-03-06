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
from openerp.report import report_sxw
from openerp import models, fields, api
from openerp.osv import orm, fields, osv



from datetime import date 
#import pdb
import logging
_logger = logging.getLogger(__name__)

class product_template(osv.osv):

    _inherit = 'product.template' 

    def _set_list_price_price(self, cr, uid, product_tmpl_id, value, context=None):
        ''' Store the standard price change in order to be able to retrieve the list_price of a product template for a given date'''
        if context is None:
            context = {}
        price_history_obj = self.pool['product.sale.price.history']
        user_company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        company_id = context.get('force_company', user_company)
        price_history_obj.create(cr, uid, {
            'product_template_id': product_tmpl_id,
            'list_price': value,
            'company_id': company_id,
        }, context=context)
    def create(self, cr, uid, vals, context=None):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        product_template_id = super(product_template, self).create(cr, uid, vals, context=context)
        self._set_list_price_price(cr, uid, product_template_id, vals.get('list_price', 0.0), context=context)

        return product_template_id
    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the list_price of a product template for a given date'''
        if isinstance(ids, (int, long)):
            ids = [ids]
        if 'list_price' in vals:
            for prod_template_id in ids:
                self._set_list_price_price(cr, uid, prod_template_id, vals['list_price'], context=context)

        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return res


class product_product(osv.osv):

    _name = 'product.product'
    _inherit = 'product.product' 



    def get_price_pricelist(self,id,pricelist):
        return 1



    def ba_price_frendly_style(self,price):
        if isinstance(price,float):
            price=round(price,2)
        price_text=str(price).split('.')
        return "$ " + price_text[0] + "<sup>" + price_text[1] + "</sup>"
 

    def _fnct_pricelist_price(self, cr, uid, ids, field_name, args, context=None):
        product_pricelist_obj = self.pool.get('product.pricelist')
        tax_obj = self.pool.get('account.tax')



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
                    res[product.id] =str('%.2f' % (price_pricelist[2] + sum_tax) )

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
                        res[product.id]+=   conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[31] + sum_tax)) + "  | "             
                    else :
                        res[product.id]+= conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[31] + sum_tax) / conditions_id['fee']) + ' (Total: ' +"${0:.2f}".format((price_pricelist[31] + sum_tax))  + ') | ' 

            for pricelist_child in product_pricelist['pricelist_id_set'] :                
                price_pricelist=self.pool.get('product.pricelist').price_get(cr,uid,[pricelist_child['id']],product.id,1.0,1,{'uom':1,'date':unicode(date.today())})
                sum_tax = 0
                for tax in product.taxes_id:
                    sum_tax += price_pricelist[pricelist_child['id']] * tax.amount
                    for conditions_id in pricelist_child['pricelist_sale_condition'] :
                        if conditions_id['fee'] == 1 :
                            res[product.id]+=   conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[pricelist_child['id']] + sum_tax)) + "  | "             
                        else :
                            res[product.id]+= conditions_id['description'] + ' ' + "${0:.2f}".format((price_pricelist[pricelist_child['id']] + sum_tax) / conditions_id['fee']) + ' (Total: ' +"${0:.2f}".format((price_pricelist[pricelist_child['id']] + sum_tax))  + ') | ' 
        return res





    _columns = {
        'total_price': fields.function(_fnct_pricelist_price, string='Precio con impuestos',type='char', size=256,),
        'total_price_condition_text': fields.function(_fnct_sales_condition_text, string='condiciones',type='text',),
    }


class produce_sale_price_history(osv.osv):
    """
    Keep track of the ``product.template`` sale prices as they are changed.
    """

    _name = 'product.sale.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'

    _columns = {
        'company_id': fields.many2one('res.company', required=True),
        'product_template_id': fields.many2one('product.template', 'Product Template', required=True, ondelete='cascade'),
        'datetime': fields.datetime('Historization Time'),
        'list_price': fields.float('Historized list price'),
    }

    def _get_default_company(self, cr, uid, context=None):
        if 'force_company' in context:
            return context['force_company']
        else:
            company = self.pool['res.users'].browse(cr, uid, uid,
                context=context).company_id
            return company.id if company else False

    _defaults = {
        'datetime': fields.datetime.now,
        'company_id': _get_default_company,
    }

