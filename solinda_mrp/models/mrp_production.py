from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    trans_date = fields.Datetime(string='Transaction Date',default=fields.Datetime.now(),required=True,readonly=True,)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mrp.production')
        return super(MrpProduction, self).create(vals)

    @api.depends('move_raw_ids.total_cost', 'workorder_ids.total_cost')
    def _compute_total_cost(self):
        for line in self:
            total_material = 0
            total_operation = 0
            total = 0
            for move in line.move_raw_ids:
                total_material += move.total_cost
            for op in line.workorder_ids:
                total_operation += op.total_cost
            total = total_operation + total_material
            line.total_cost = total
            
    customer = fields.Many2one(related='bom_id.customer', string='Customer', store=True)
    retail_price = fields.Float(related='bom_id.retail_price', string='Retail Price', store=True)
    sales_order_id = fields.Many2one('sale.order', string='SO No.')
    po_no = fields.Char(string='PO No.')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    delivery_date = fields.Date(string="Delivery")
    product_tmpl_id = fields.Many2one('product.template', string='Product',related="product_id.product_tmpl_id")
    move_byproduct_ids = fields.One2many('stock.move')
    # move_byproduct_ids = fields.One2many('stock.move', compute='_compute_move_byproduct_ids', inverse='_set_move_byproduct_ids')

    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

