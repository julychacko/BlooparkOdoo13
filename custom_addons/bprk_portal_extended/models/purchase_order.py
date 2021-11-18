from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    request_id = fields.Many2one("product.order.request")


    def action_view_request(self):
        for record in self:
            return {
                'name': _('Request Details'),
                'view_mode': "form",
                'res_model': 'product.order.request',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': record.request_id.id,
            }