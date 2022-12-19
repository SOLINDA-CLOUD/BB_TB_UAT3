from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    # state = fields.Selection(selection_add=[('approve', 'Approved')], ondelete={'approv': 'cascade'})
    state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('approve', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    state_bill = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    def action_post(self):
        res = super(AccountMove,self).action_post()
        self.state_bill = 'posted'
        return res


    def approve_posted_bill(self):
        self.state_bill = 'approve'