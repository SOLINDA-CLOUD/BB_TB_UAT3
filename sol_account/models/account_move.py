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
            ('approve', 'Approved'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ], string='Status', related="state", required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.onchange('state')
    def _onchange_state(self):
        self.state_bill = self.state

    def approve_posted_bill(self):
        self.state = 'approve'