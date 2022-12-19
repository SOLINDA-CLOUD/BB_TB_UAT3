from odoo import _, api, fields, models

class ByProductDummy(models.Model):
    _name = 'by.product.dummy'
    _description = 'By Product Dummy'
    
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', string='UoM')
    product_uom_qty = fields.Float(string='Produce', default=1)
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

class MrpProductionBomVariant(models.Model):
    _name = 'mrp.production.bom.variant'
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = 'Bill of Material MRP (Variant)'

    @api.depends('product_qty', 'cost')
    def _compute_total_material(self):
        for line in self:
            line.total_material = line.cost * line.product_qty

    company_id = fields.Many2one(
        related='production_id.company_id', store=True, index=True, readonly=True)
    product_id = fields.Many2one('product.product', 'Component', required=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    po_qty = fields.Float(
        'Qty PO', default=0.0,
        digits='Product Unit of Measure', required=True)
    total_qty = fields.Float(
        'Total', default=0.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    production_id = fields.Many2one(
        'mrp.production', 'MRP Production',
        index=True, ondelete='cascade', required=True)
    supplier = fields.Many2one('res.partner',string='Supplier')
    color = fields.Char('Color')
    sizes = fields.Char('Sizes')
    ratio = fields.Float(string='Ratio', default=1.00)
    cost = fields.Float(string="Cost", related='product_id.standard_price')
    total_material = fields.Float(string="Total Material", compute=_compute_total_material)
            

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    by_product_ids = fields.One2many('by.product.dummy', 'mrp_id', string='By Product')
    purchase_request_id = fields.Many2one('purchase.request', string='Sample Development')
    is_sample = fields.Boolean('Is Sample')
    mrp_bom_variant_ids = fields.One2many('mrp.production.bom.variant', 'production_id', 'Material Variant', copy=True)
    total_qty = fields.Float(string="Total Qty", compute="_compute_total_qty_dummy")
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)
    retail_price = fields.Float(related='bom_id.retail_price', string='Retail Price', store=True)
    roi = fields.Float(string="ROI", compute="_compute_roi")

    @api.depends('retail_price', 'total_cost', 'total_qty')
    def _compute_roi(self):
        for line in self:
            total_wholesale = line.retail_price * line.total_qty
            line.roi = (total_wholesale - line.total_cost) * 100 / total_wholesale

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

    @api.depends('by_product_ids.product_uom_qty')
    def _compute_total_qty_dummy(self):
        for by in self:
            if by.by_product_ids:
                total = 0
                for line in by.by_product_ids:
                    total += line.product_uom_qty
                by.total_qty = total
            else:
                by.total_qty = 0
    

    def update_qty_consume_with_variant(self):
        for move in self.move_raw_ids:
            qty_consume = 0
            sql ='''select pp.product_tmpl_id as product_tmpl_id,
                            mv.sizes as size_variant, 
                            md.size as size_dummy, 
                            mv.product_qty as qty_variant, 
                            md.product_uom_qty as qty_dummy,
                            mv.product_qty*md.product_uom_qty as qty_consume
                    from mrp_production_bom_variant mv
                    inner join by_product_dummy md on md.mrp_id=mv.production_id
                    inner join product_product pp on pp.id=mv.product_id
                    where mv.sizes = md.size and mv.production_id=%s and md.mrp_id=%s
                    '''% (self.id,self.id)
            self.env.cr.execute(sql)
            data = self.env.cr.dictfetchall()
            for d in data:
                product_tmpl_id = d['product_tmpl_id']
                sizes = d['size_variant']
                qty_variant = d['qty_variant']
                qty_dummy = d['qty_dummy']
                total_qty = d['qty_consume']
                for var in self.mrp_bom_variant_ids:
                    if var.product_id.product_tmpl_id.id == product_tmpl_id and var.sizes == sizes:
                        var.po_qty = qty_dummy
                        var.total_qty = total_qty
                    else:
                        var.total_qty = var.po_qty * var.product_qty
                if move.product_id.product_tmpl_id.id == product_tmpl_id:
                    qty_consume += d['qty_consume']
                    move.product_uom_qty = qty_consume

    def _create_workorder(self):
        for production in self:
            if not production.bom_id or not production.product_id:
                continue
            workorders_values = []

            product_qty = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
            exploded_boms, dummy = production.bom_id.explode(production.product_id, product_qty / production.bom_id.product_qty, picking_type=production.bom_id.picking_type_id)

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom BoM are the same, don't recreate work orders.
                if not (bom.operation_ids and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.operation_ids != bom.operation_ids)):
                    continue
                for operation in bom.operation_ids:
                    # accessories_ids = []
                    # for accessories in operation.accessories_ids:
                    #     accessories_ids.append((4, accessories.id, None))

                    accessories_ids = []
                    for accessories in operation.fabric_id:
                        accessories_ids.append((4, accessories.id, None))

                    if operation._skip_operation_line(bom_data['product']):
                        continue
                    workorders_values += [{
                        'name': operation.name,
                        'production_id': production.id,
                        'workcenter_id': operation.workcenter_id.id,
                        'product_uom_id': production.product_uom_id.id,
                        'operation_id': operation.id,
                        'state': 'pending',
                        # 'accessories_ids': accessories_ids,
                        'fabric_id': accessories_ids,
                    }]

            production.workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()

    