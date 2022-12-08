from odoo import _, api, fields, models

class ByProductDummy(models.Model):
    _name = 'by.product.dummy'
    _description = 'By Product Dummy'
    
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    product_uom_qty = fields.Float(string='Produce')
    product_minus = fields.Float(string='Not Produce')
    colour = fields.Char('Color')
    size = fields.Char('Size')
    remarks = fields.Text('Remarks')
    mrp_id = fields.Many2one('mrp.production', string='MRP')
    fabric_por_id = fields.Many2one('product.product', string='Fabric')
    lining_por_id = fields.Many2one('product.product', string='Lining')

    @api.onchange('product_minus')
    def _onchange_product_minus(self):
        for i in self:
            if i.product_minus > 0:
                by_prod = self.env["stock.move"].search([('product_id', '=', self.product_id.id),('production_id', '=', self._origin.mrp_id.id)],limit=1)
                if by_prod:
                    by_prod.product_uom_qty = self.product_uom_qty - i.product_minus
                else:
                    self.mrp_id.product_qty = self.mrp_id.product_qty - i.product_minus
                    
    @api.onchange('product_uom_qty')
    def _onchange_product_uom_qty(self):
        by_prod = self.env["stock.move"].search([('product_id', '=', self.product_id.id),('production_id', '=', self._origin.mrp_id.id)],limit=1)
        if by_prod:
            by_prod.product_uom_qty = self.product_uom_qty
        else:
            self.mrp_id.product_qty = self.product_uom_qty
            

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    by_product_ids = fields.One2many('by.product.dummy', 'mrp_id', string='By Product')
    purchase_request_id = fields.Many2one('purchase.request', string='Sample Development')
    is_sample = fields.Boolean('Is Sample')


    
    