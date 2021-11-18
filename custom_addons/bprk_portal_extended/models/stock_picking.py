from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_date = fields.Date('Picking Date')

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for record in self:
            if record.origin:
                purchase_order = self.env['purchase.order'].sudo().search([('name','=',record.origin)])
                if purchase_order and purchase_order.request_id:
                    purchase_order.request_id.write({
                        'state':'ready_pick_up',
                        'picking_id':record.id
                        })
                    try:
                        purchase_order.request_id.product_receival_notify_employee()
                    except:
                        pass
            
        return res