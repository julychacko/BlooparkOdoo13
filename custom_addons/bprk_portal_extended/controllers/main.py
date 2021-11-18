import logging
import werkzeug
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import dateutil.parser

from odoo import fields, http, _
from odoo.http import request, route
from odoo.osv import expression
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)
import ast
from odoo.http import request, route, content_disposition
from odoo.tools import frozendict
from odoo.exceptions import AccessError, MissingError
import base64
import json
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager

class CustomerPortal(CustomerPortal):

    @http.route("/website/menu", type="json",
                auth="user", website=True)
    def get_dashboard_menu(self, user_id):
        user = request.env['res.users'].sudo().search([('id', '=', user_id)])
        if user.has_group('bprk_portal_extended.group_manager') or user.has_group('bprk_portal_extended.group_employee'):
            return True
        return False


    @http.route(['/my/portal','/my/portal/page/<int:page>'],
                type='http',
                auth="user", website=True)
    def my_portal_dashboard(self,page=1, **post):
        user = request.env.user
        product_requests_count = len(request.env['product.order.request'].search([],order="id desc"))
        
        pager = portal_pager(
            url="/my/portal",
            url_args={},
            total=product_requests_count,
            page=page,
            step=10
        )

        product_requests = request.env['product.order.request'].search([],order="id desc",limit=10,offset=pager['offset'])

        

        post.update({
            'user':user,
            'product_requests':product_requests,
            'pager':pager
            })
        return request.render("bprk_portal_extended.my_portal_dashboard",post)

    @http.route('/CreateRequest', type='http', auth='user', website=True)
    def render_request_creation(self, **kw):
        values ={}
        user = request.env.user
        products = http.request.env['product.product'].sudo().search([('categ_id.id','child_of',user.allowed_categories.ids)])
        
        values.update({
            'products': products,
            'current_date': fields.Date.today().strftime("%Y %B %d"),
            'user':user
        })
        return http.request.render('bprk_portal_extended.template_product_request', values)

    @http.route('/product_request_form', type='http', auth='user', website=True)
    def render_request_submission(self, **kw):
        user = request.env.user
        product_order_request_obj = request.env['product.order.request'].sudo()

        product = False
        if kw.get("product_id",False):
            product = request.env['product.product'].sudo().browse(int(kw['product_id']))

        supplier = False
        if kw.get("selected_supplier",False):
            supplier_prod_line = request.env['product.supplierinfo'].sudo().browse(int(kw['selected_supplier']))
            if supplier_prod_line:
                supplier = supplier_prod_line.sudo().name.id

        values = {
            'employee_id':user.id,
            'desc':kw.get("desc",""),
            'product_id':product and product.sudo().id or False,
            "product_supplier_id":kw.get("selected_supplier",False),
            'net_price':kw.get("net_price",0),
            "gross_price":kw.get("gross_price",0),
            'tax_amount': kw.get("amount_tax",0),
            'supplier_id':supplier
            }
        if kw.get("attachment_id",False):
            values.update({
                'attachment_ids':  [(6, 0, [int(kw['attachment_id'])])]
                })
        if user.custom_tax_ids:
            values.update({'tax_ids':[(6,0, user.custom_tax_ids.ids)]})
        elif product and product.taxes_id:
            values.update({'tax_ids':[(6,0, product.taxes_id.ids)]})

        prod_request = product_order_request_obj.create(values)

        return http.request.render('bprk_portal_extended.success_product_request', {})


    @http.route('/my/productrequest/<request_id>', type='http', auth='user', website=True)
    def render_view_product_request(self, request_id,access_token=None, **kw):
        values = {}
        request_sudo = False

        try:
            request_sudo = self._document_check_access('product.order.request', int(request_id), access_token=access_token)
        except (AccessError, MissingError) as e:
            return werkzeug.utils.redirect("/my/portal")
        
        values.update({
            'request_obj':request_sudo,
            'user':request.env.user,
            })
        
        return http.request.render('bprk_portal_extended.template_product_request_view', values)


    @http.route('/PerformAction', type='http', auth='user', website=True)
    def render_perform_action(self, access_token=None, **kw):
        values = {}
        request_sudo = False

        if kw.get("request_id",False) and kw.get("action",""):
            request_id = kw['request_id']
            action = kw['action']

            try:
                request_sudo = self._document_check_access('product.order.request', int(request_id), access_token=access_token)
            except (AccessError, MissingError) as e:
                return werkzeug.utils.redirect("/my/portal")

            if action == 'approve':
                request_sudo.approve_request()
            elif action == 'reject':
                request_sudo.reject_request()
            elif action == 'buy':
                request_sudo.buy_product()
            elif action == 'pickup':
                request_sudo.mark_as_done()
            
        
        return werkzeug.utils.redirect("/my/portal")

    @http.route(['/fileupload'], type='http', auth='user', website=True, csrf=False)
    def ticket_file_upload(self, **kw):
        """
        File Upload - * Dropzone:
        """
        result = {}
        if kw.get('file',False):
            file = kw['file']
            if type(file) == werkzeug.datastructures.FileStorage:
                image_binary = (file.read())
                file_data = {'datas': base64.encodestring(image_binary),'name':file.filename}
                attachment = request.env['ir.attachment'].sudo().create(file_data)
                if attachment:
                    result.update({'attachment_id':attachment.id})
                
        return json.dumps(result)

    # remove a file
    @http.route(['/remove/file/<file_dict>'], type='http', auth="user", website=True, csrf=False)
    def render_remove_file(self, file_dict, **kw):
        try:
            values = ast.literal_eval(file_dict)
            if values.get('attachment_id',False):
                attachment = request.env['ir.attachment'].sudo().search([('id','=',values['attachment_id'])])
                if attachment:
                    attachment.unlink()
        except:
            pass
        
        return json.dumps({'result':True})
            
