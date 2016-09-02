# -*- coding: utf-8 -*-
from openerp.osv import orm, osv, fields

from datetime import date

import logging
_logger = logging.getLogger(__name__)


class product_watching_products(osv.osv):
    _name = "product.watching.products"

    _description = "watching products"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'section_id' : fields.many2one('crm.case.section','section'),
        'report' : fields.selection([('report_label_watching_product','Etiquetas gondola'),
                                     ('report_corner_watching_product','Etiquetas Corner'),
                                     ('report_table_watching_product','Etiquetas mueble'),
                                     ('report_full_watching_product','Hoja completa'),

                                     ],'Etiqueta'),
        'email' : fields.char('Email'),

        'product_id' : fields.many2many('product.product','watching_products_rel','list_id','product_id','Products'),

        'last_print' : fields.datetime('Ultima impresion'),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the payment term without removing it."),
    }

    _defaults = {
        'active': 1,
    }
    _order = 'name'

    def watching_products_action_label(self, cr, uid, context=None):

        #watching_products_obj = self.pool.get('product.watching.products')
        watching_products_ids = self.search( cr, uid,[('active','=',True)])
        mail_mail_obj = self.pool.get('mail.mail')

        attachment_obj = self.pool.get('ir.attachment')
        ir_actions_report = self.pool.get('ir.actions.report.xml')



        for watching_products in self.browse(cr,uid,watching_products_ids):
            report=self.watching_products_all_label( cr, uid, [watching_products['id']], context=None)

            if report : 

                _logger.info("report %r" ,report)
                attachment_id = attachment_obj.create(cr, uid,
                              {
                                  'name': report['report_name'],
                                  'datas': report,
                                  'datas_fname': report['report_name'],
                                  'type': 'binary'
                              }, context=context)


                # post the message
                values = {
                    'model': None,
                    'res_id': None,
                    'subject': u"Actualizaciones " + watching_products['name'],
                    'body': 'Actualizaciones de precios',
                    'body_html': 'Actualizaciones de precios',
                    'parent_id': None,
                    'partner_ids':  None,
                    'notified_partner_ids': None,
                    'attachment_ids': None,
                    'email_from': 'consultas@blancoamor.com',
                    'email_to': 'filoquin@gmail.com',
                }
                mail_id = mail_mail_obj.create(cr, uid, values, context=context)
                mail_mail_obj.send(cr, uid, [mail_id], context=context)






    def watching_products_all_label(self, cr, uid, ids, context=None):
        #product_watching_products_obj = self.pool.get('product.watching.products')

        product_products_obj = self.pool.get('product.product')
        cur_obj = self.browse(cr, uid, ids, context=context)
        datas = {}
        items_ids=[]
        for item in cur_obj.product_id:
            items_ids.append(item.id)

        #product_ids = product_products_obj.search(cr, uid, [('id', 'in', cur_obj.student_id.fname),
        #    ('write_date','>=',cur_obj.start_date)], context=context)

        product_ids = product_products_obj.search(cr, uid, [('id', 'in',items_ids)], context=context)
        _logger.info("watching_products_label %r " , product_ids )
        
        values={'last_print':date.today()}

        self.write(cr, uid, ids, values,context=context)
        if product_ids:
            data = self.read(cr, uid, ids, context=context)[0]

            datas = {
            'ids': product_ids,
            'model': 'product.product', 
            'form': data,
            'context':context
            }

            return {
                   'type': 'ir.actions.report.xml',
                   'model': 'product.product', 
                   'report_name': 'ba_watching_products.'+ cur_obj.report,
                   'datas': datas,
               }    

    def watching_products_label(self, cr, uid, ids, context=None):
        #product_watching_products_obj = self.pool.get('product.watching.products')
        product_products_obj = self.pool.get('product.product')
        cur_obj = self.browse(cr, uid, ids, context=context)
  
        datas = {}
        items_ids=[]
        for item in cur_obj.product_id:
            items_ids.append(item.id)

        #product_ids = product_products_obj.search(cr, uid, [('id', 'in', cur_obj.student_id.fname),
        #    ('write_date','>=',cur_obj.start_date)], context=context)

        product_ids = product_products_obj.search(cr, uid, [('id', 'in',items_ids),('write_date','>=',cur_obj.last_print)], context=context)
        
        values={'last_print':date.today()}

        self.write(cr, uid, ids, values,context=context)
        if product_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            datas = {
            'ids': product_ids,
            'model': 'wiz.watching.products', 
            'form': data,
            'context':context
            }
            return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ba_watching_products.'+ cur_obj.report,
                   'datas': datas,
               }    

class wiz_watching_products(orm.TransientModel):
    _name = 'wiz.watching.products'
    _columns = {
        'list_id': fields.many2one('product.watching.products', 'List'),
        'start_date': fields.datetime('Start Date'),
    }


    def watching_products_report(self, cr, uid, ids, context=None):
        product_watching_products_obj = self.pool.get('product.watching.products')
        product_products_obj = self.pool.get('product.product')
        cur_obj = self.browse(cr, uid, ids, context=context)
        datas = {}
        items_ids=[]
        for item in cur_obj.list_id.product_id:
            items_ids.append(item.id)

        #product_ids = product_products_obj.search(cr, uid, [('id', 'in', cur_obj.student_id.fname),
        #    ('write_date','>=',cur_obj.start_date)], context=context)

        product_ids = product_products_obj.search(cr, uid, [('id', 'in',items_ids),('write_date','>=',cur_obj.start_date)], context=context)
 

        if product_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            datas = {
            'ids': product_ids,
            'model': 'wiz.watching.products', 
            'form': data,
            'context':context
            }
            return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ba_watching_products.report_label_watching_product',
                   'datas': datas,
               }    