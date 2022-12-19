from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    trans_date = fields.Datetime(string='Transaction Date',default=fields.Datetime.now(),required=True,readonly=True,)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('mrp.production')
        return super(MrpProduction, self).create(vals)

   

    
            
    customer = fields.Many2one(related='bom_id.customer', string='Customer', store=True)
    
    sales_order_id = fields.Many2one('sale.order', string='SO No.')
    po_no = fields.Char(string='PO No.')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    delivery_date = fields.Date(string="Delivery")
    product_tmpl_id = fields.Many2one('product.template', string='Product',related="product_id.product_tmpl_id")
    move_byproduct_ids = fields.One2many('stock.move')
    # move_byproduct_ids = fields.One2many('stock.move', compute='_compute_move_byproduct_ids', inverse='_set_move_byproduct_ids')

    
    
