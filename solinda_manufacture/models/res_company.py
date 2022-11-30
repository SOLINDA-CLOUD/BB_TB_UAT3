from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    is_manufacturing = fields.Boolean('Manufacturing', help="define the company place for manage manufacturing or not")