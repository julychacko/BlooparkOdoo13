from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)


class ProductOrderRequest(models.Model):
    _name = 'product.order.request'
    _description = 'Product Order Request'
    _order = 'id desc'

    name = fields.Char('Name')
    state = fields.Selection([
        ('draft','Draft'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('purchase_in_progress','Purchase in progress'),
        ('ready_pick_up','Ready to pick-up'),
        ('done','Done')
        ], default='draft',string="State")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
    product_id = fields.Many2one('product.product',string="Product")
    employee_id = fields.Many2one('res.users',string="Employee") #not integrating with employee module now, Using users model
    supplier_id = fields.Many2one('res.partner',string="Supplier")
    product_supplier_id = fields.Many2one('product.supplierinfo',string="Supplier")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', copy=False)
    desc = fields.Text("Description")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    net_price = fields.Monetary('Net Price')
    gross_price = fields.Monetary('Gross Price')
    tax_ids = fields.Many2many("account.tax", string="Tax")
    tax_amount = fields.Monetary('Tax Amount')
    order_id = fields.Many2one("purchase.order")
    picking_id = fields.Many2one("stock.picking",string="Picking")

    @api.model
    def create(self, vals):
        if not vals.get('name',False):
            vals['name'] = self.env['ir.sequence'].next_by_code('product.order.request') or _('New')
        result = super(ProductOrderRequest, self).create(vals)
        try:
            result.new_request_notify_manager()
        except:
            pass
        return result

    def approve_request(self):
        for record in self:
            record.write({'state':'approved'})
            try:
                record.approved_request_notify_employee()
            except:
                pass

        return True

    def reject_request(self):
        for record in self:
            record.write({'state':'rejected'})
            record.employee_id.write({"last_rejected_date":fields.Date.today()})
            try:
                record.rejected_request_notify_employee()
            except:
                pass
        return True

    def mark_as_done(self):
        for record in self:
            record.write({'state':'done'})
        return True

    def buy_product(self):
        for record in self:
            purchase_obj = self.env['purchase.order'].sudo()
            purchase_line_obj = self.env['purchase.order.line'].sudo()
            order_values = {
            'partner_id':record.supplier_id.sudo().id,
            'request_id':record.id,
            'partner_ref':record.name,
            }
            purchase_order = purchase_obj.create(order_values)


           

            order_line_values = {
                'product_id':record.product_id.id,
                'price_unit': record.net_price,
                'order_id':purchase_order.id,
                'name':record.product_id.display_name or record.name,
                'product_qty':1,
                'product_uom_qty':1,
                'product_uom': record.product_id.uom_po_id.id,
                'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(record.product_supplier_id.delay)),
                'taxes_id':[(6,0, record.tax_ids.ids)]
            }
            purchase_order_line = purchase_line_obj.create(order_line_values)

            record.write({'state':'purchase_in_progress',"order_id":purchase_order.id})
        return True

    def get_request_portal_url(self):
        for record in self:
            url = ""
            url += self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url += "/my/productrequest/"
            url += str(record.id)
            return url

    def action_view_order(self):
        for record in self:
            return {
                'name': _('Purchase Request'),
                'view_mode': "form",
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': record.order_id.id,
            }

    def product_receival_notify_employee(self):
        for record in self:
            user = record.employee_id
            template = False
            if not template:
                template = self.env.ref('bprk_portal_extended.email_template_product_receive_employee')
            assert template._name == 'mail.template'

            with self.env.cr.savepoint():
                template.with_context(lang=user.lang).send_mail(record.id, force_send=True, raise_exception=True)
            _logger.info("Product Receival email sent for user <%s> to <%s>", user.login, user.email)

    def new_request_notify_manager(self):
        for record in self:
            user = record.employee_id.sudo().manager_id.sudo()
            template = False
            if not template:
                template = self.env.ref('bprk_portal_extended.email_template_new_request_manager')
            assert template._name == 'mail.template'
            with self.env.cr.savepoint():
                template.with_context(lang=user.lang).send_mail(record.id, force_send=True, raise_exception=True)
            _logger.info("New Request notify to manager <%s> to <%s>", user.login, user.email)

    def approved_request_notify_employee(self):
        for record in self:
            user = record.employee_id
            template = False
            if not template:
                template = self.env.ref('bprk_portal_extended.email_template_approved_request_employee')
            assert template._name == 'mail.template'
            with self.env.cr.savepoint():
                template.with_context(lang=user.lang).send_mail(record.id, force_send=True, raise_exception=True)
            _logger.info("Approved Request notification to sent for user <%s> to <%s>", user.login, user.email)

    def rejected_request_notify_employee(self):
        for record in self:
            user = record.employee_id
            template = False
            if not template:
                template = self.env.ref('bprk_portal_extended.email_template_rejected_request_employee')
            assert template._name == 'mail.template'
            with self.env.cr.savepoint():
                template.with_context(lang=user.lang).send_mail(record.id, force_send=True, raise_exception=True)
            _logger.info("Rejected Request notification to sent for user <%s> to <%s>", user.login, user.email)