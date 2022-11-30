from odoo import fields, api, models

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, store=True, readonly=False, check_company=True, copy=True, related='move_id.partner_id.analytic_account_id')
