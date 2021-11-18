from odoo import models, fields, api, _
import datetime

class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_categories = fields.Many2many('product.category', string="Allowed Categories")
    custom_tax_ids = fields.Many2many('account.tax', string="Custom Tax")
    manager_id = fields.Many2one('res.users',string="Manager")
    last_rejected_date = fields.Date("Request Rejected Date")

    @api.model
    def create(self, vals):
        if self._context.get('is_employee', False):
            # We can use employee module here in future and can link with portal user with employee
            groups = {'groups_id': [(6, 0, [
                self.env.ref('bprk_portal_extended.group_employee').id,
                ])]}
            vals.update(groups)
        if self._context.get('is_internal_user', False):
            groups = {'groups_id': [(6, 0, [self.env.ref('purchase.group_purchase_manager').id,self.env.ref('stock.group_stock_manager').id,self.env.ref('bprk_portal_extended.group_internal_user').id])]}
            vals.update(groups)
        if self._context.get('is_manager', False):
            groups = {'groups_id': [(6, 0, [
                self.env.ref('bprk_portal_extended.group_manager').id,
                ])]}
            vals.update(groups)
        return super(ResUsers, self).create(vals)

    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):

        user_ids = super(ResUsers, self)._search(args, offset=offset, limit=None, order=order, count=False,
                                                 access_rights_uid=access_rights_uid)

        managers = self._context.get('is_manager', False)
        internal_users = self._context.get('is_internal_user', False)
        employees = self._context.get('is_employee', False)

        user_list = []

        if self._context.get('default_value', False):
            return user_ids

        if managers:
            for user in self.env['res.users'].browse(user_ids):
                if user.has_group('bprk_portal_extended.group_manager'):
                    user_list.append(user.id)
            return user_list

        if internal_users:
            for user in self.env['res.users'].browse(user_ids):
                if user.has_group('bprk_portal_extended.group_internal_user'):
                    user_list.append(user.id)
            return user_list

        if employees:
            for user in self.env['res.users'].browse(user_ids):
                if user.has_group('bprk_portal_extended.group_employee'):
                    user_list.append(user.id)
            return user_list
        

        return user_ids

    @api.model
    def check_request_rejected_date(self):
        user = self.env.user
        status = True
        if user.last_rejected_date:
            start_date = datetime.datetime.now() - datetime.timedelta(30)
            if (start_date.date() < user.last_rejected_date):
                return False
        return status