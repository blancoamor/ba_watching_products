# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import orm, osv, fields

from datetime import date , datetime

import logging
_logger = logging.getLogger(__name__)


class product_watching_products(osv.osv):
    _name = "product.watching.products"
    _inherit = "mail.thread"


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
        email_template_obj = self.pool.get('email.template')

        attachment_obj = self.pool.get('ir.attachment')

        

        for watching_products in self.browse(cr,uid,watching_products_ids):


            mail_ids = []
            attachment_ids = []
            email_to = "filoquin@gmail.com"  
            attachment_data = {
                'name': "Report Data",
                'datas_fname': 'r.pdf', # your object File Name
                'db_datas': {
                   'report_name': 'ba_watching_products.'+ watching_products['report'],
                   'datas': { 'ids': watching_products['product_id'],'model':'product.product'},
               } 
            }
            attachment_ids.append (attachment_obj.create(cr, uid, attachment_data, context=context))
            _logger.info("attachment_ids %r" , attachment_ids)
            mail_ids.append (mail_mail_obj.create(cr, uid,
                {
                   'email_to': email_to,
                   'subject': 'reporte',
                   'body_html': '<pre>hoka</pre>' ,
                }, context = context))
            if attachment_ids:

                mail_mail_obj.write(cr, uid, mail_ids, {'attachment_ids': [(6, 0, attachment_ids)]}, context=context)
            mail_mail_obj.send (cr, uid, mail_ids, context = context)

   



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
        
        values={'last_print':datetime.now()}

        title='Impresion completa'
        self.message_post(cr,uid,cur_obj['id'], 'Se genero un pdf con todos los articulos de la lista y se actualizo la fecha de impresion',title)


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

    def watching_products_label(self, cr, uid, ids, context=None):
        #product_watching_products_obj = self.pool.get('product.watching.products')
        product_products_obj = self.pool.get('product.product')
        price_history_obj = self.pool.get('product.price.history')
        cur_obj = self.browse(cr, uid, ids, context=context)
  
        datas = {}
        product_ids =[]
        items_ids=[]
        changes=[]
        for item in cur_obj.product_id:
            #price_history_ids=price_history_obj.search(cr,uid,[('datetime','>=',cur_obj.last_print),('product_template_id','=',item.product_tmpl_id.id)])
            #obtengo el ultimo cambio anterior a la impresion
            price_history_ids=price_history_obj.search(cr,uid,[('datetime','<=',cur_obj.last_print),
                                                               ('product_template_id','=',item.product_tmpl_id.id)],
                                                                order='datetime desc', limit=1)
            for history in price_history_obj.browse(cr,uid,price_history_ids):
                _logger.info('%s anterior %s actualizado a %s' % (item.default_code,history.cost , item.standard_price))
                if int(history.cost) != int(item.standard_price):
                    changes.append(u'%s anterior %s actualizado a %s' % (item.default_code,history.cost , item.standard_price))
                    product_ids.append(item.id)
                    break


        #product_ids = product_products_obj.search(cr, uid, [('id', 'in', cur_obj.student_id.fname),
        #    ('write_date','>=',cur_obj.start_date)], context=context)

        #product_ids = product_products_obj.search(cr, uid, [('id', 'in',items_ids),('write_date','>=',cur_obj.last_print)], context=context)
        


        if product_ids:
            values={'last_print':datetime.now()}

            self.write(cr, uid, ids, values,context=context)
            title='Impresion Parcial'

            self.message_post(cr,uid,cur_obj['id'],  u'Se genero un pdf con los articulos que se actualizaron y se actualizo la fecha de impresión ' + "|".join(changes),title)

            data = self.read(cr, uid, ids, context=context)[0]
            datas = {
            'ids': product_ids,
            'model': 'wiz.watching.products', 
            'form': data,
            'context':context,
            'attachment_use':True
            }
            return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'ba_watching_products.'+ cur_obj.report,
                   'datas': datas,
               } 
        else:
            title='Sin nada que imprimir'
            self.message_post(cr,uid,cur_obj['id'],  'No se genero un pdf con los articulos que se actualizaron y no se actualizo la fecha de impresión',title)

            return {
                    'type': 'ir.actions.client',
                    'tag': 'action_warn',
                    'name': 'Warning',
                    'params': {
                       'title': 'Sin nada que imprimir!',
                       'text': 'No se genero un pdf con los articulos que se actualizaron y no se actualizo la fecha de impresión.',
                       'sticky': True
                    }
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