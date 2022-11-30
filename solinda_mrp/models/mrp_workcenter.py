from odoo import fields, api, models

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    product_service_id = fields.Many2one(
        comodel_name='product.product',
        domain=[('type', '=', 'consu')],
        string='Product'
        )

    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure',
        help="Default unit of measure used for all stock operations.")
