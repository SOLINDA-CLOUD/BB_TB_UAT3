# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    # name = fields.Char(string='Reference', states={'open': [('readonly', False)]}, copy=False, readonly=True)
    name = fields.Char(
        required=False,
        default='New',
        index=True,
        readonly=True,
        string='Reference'
    )
    balance_end_real = fields.Monetary('Ending Balance', states={'confirm': [('readonly', True)]}, compute='_compute_ending_balance', recursive=True, readonly=False, store=True, tracking=True)

    @api.model
    def create(self, vals):
        self = self.sudo()
        iterate = self.env['ir.sequence'].next_by_code('account.bank.statement')
        if iterate:
            vals['name'] = iterate
        else:
            vals['name'] = 'New'
        return super(AccountBankStatement, self).create(vals)
    
    @api.onchange('balance_end')
    def _onchange_balance_end(self):
        for line in self:
            line.balance_end_real = line.balance_end