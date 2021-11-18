from odoo import models, fields, api, _

class Product(models.Model):
	_inherit = 'product.product'

	@api.model
	def get_product_suppliers(self, product_id):
		content = ""
		if product_id:
			product = self.sudo().search([('id','=',int(product_id))])
			if product:
				for supplier in product.product_tmpl_id.variant_seller_ids:
					content += "<tr>"
					content += "<td>"
					content += supplier.name.name
					content += "</td>"
					content += "<td>"
					content += str(supplier.min_qty)
					content += "</td>"
					content += "<td>"
					content += str(supplier.price)
					content += "</td>"
					content += "<td>"
					content += "<input type='radio' name='selected_supplier' value='"+str(supplier.id)+"' id='"+"selected_supplier_"+str(supplier.id)+"' />"
					content += "<label class='' for='"+"selected_supplier_"+str(supplier.id)+"'></label>"
					# content += "<span class='graphical-radio'></span>"
					# content += "<span class='radiobtn'></span>"
					content += "</td>"
					content += "</tr>"
		return content

	@api.model
	def get_product_prices(self, supplier_id):
		values = {'net_price':0,'gross_price':0,'tax_amount':0,'tax_name':""}
		user = self.env.user
		if supplier_id:
			supplier_info = self.env['product.supplierinfo'].sudo().search([('id','=',int(supplier_id))])
			if supplier_info:
				net_price = supplier_info.price / supplier_info.min_qty
				if net_price:
					tax_ids = user.custom_tax_ids or supplier_info.product_id.taxes_id
					taxes = tax_ids.compute_all(net_price,user.company_id.currency_id,1,
			                supplier_info.product_id.id,
			                user.partner_id)
					price_tax = sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
					tax_name = ""
					for t in taxes.get('taxes', []):
						if tax_name:
							tax_name += ","+t.get('name', "") 
						else:
							tax_name += t.get('name', "") 
					values.update({
						'net_price':net_price,
						'tax_amount':price_tax,
						'gross_price':net_price + price_tax,
						"tax_name":tax_name
						})
		return values