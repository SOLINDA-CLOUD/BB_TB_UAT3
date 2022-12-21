from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'

    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account', store=True)

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Partner,self).create(vals_list)
        if res['company_type'] == 'company':
            analytic = self.env['account.analytic.account'].create({
                    'name': res.name,
                    'partner_id': res.id
                })
            res.update({'analytic_account_id': analytic.id})
        return res