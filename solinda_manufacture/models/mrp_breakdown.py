from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class VariantDetail(models.Model):
    _name = 'variant.detail'
    _description = 'Variant Detail'
    
    product_id = fields.Many2one('product.product', string='Product')
    product_template_variant_value_ids = fields.Many2many('product.template.variant.value', string='Variant')
    product_qty = fields.Float('Quantity To Produce',default=1.0, digits='Product Unit of Measure',readonly=True, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',related="product_id.uom_id")
    breakdown_id = fields.Many2one('mrp.breakdown', string='Breakdown')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for i in self:
            i.write({
                'product_template_variant_value_ids' : [(6,0,i.product_id.product_template_variant_value_ids.ids)],
                'uom_id' : i.product_id.uom_id.id
            })

class MrpBreakdownLine(models.Model):
    _name = 'mrp.breakdown.line'
    _description = 'Mrp Breakdown Line'

    name = fields.Char('Name')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    breakdown_id = fields.Many2one('mrp.breakdown', string='Breakdown')
    fabric_id = fields.Many2one('mrp.bom.line', string='Fabric')
    color = fields.Char('Color')
    hk = fields.Float('HK')
    shrink_age = fields.Float('Shrink Age')
    product_id = fields.Many2one('product.product', string='Product')
    state = fields.Selection([
        ('pending', 'Waiting for another WO'),
        ('waiting', 'Waiting for components'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status',
        store=True,default='pending', copy=False, readonly=True)

    def show_receive_po(self):
        self.purchase_id.action_view_picking()

    def show_po(self):
        if not self.purchase_id:
            raise ValidationError("PO is not defined!\nPlease create PO first")
        return {
                'name': _("Purchase Order"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                # 'target': 'new',
                'res_id': self.purchase_id.id,
            } 

    def create_po(self):
        for i in self:
            raw_po_line = []
            i.button_start()
            if not i.supplier:
                raise ValidationError("Please input the supplier first")
            po = i.env['purchase.order'].create({'partner_id': i.supplier.id,'state': 'draft','date_approve': datetime.now()})
            if po:
                i.order_id = po.id
            raw_po_line.append((0,0, {
                'product_id': i.workcenter_id.product_service_id.id,
                # 'fabric': i.fabric_id.product_id.name,
                'lining':'',
                'color':i.color_id.name,
                'product_qty': i.qty_producing,
            }))           
            i.show_po()
            po.update({"order_line": raw_po_line})
            

class ComponenBreakdown(models.Model):
    _name = 'component.breakdown'
    _description = 'Componen Breakdown'
    
    product_id = fields.Many2one('product.product', string='Product')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    color = fields.Char('Color')
    hk = fields.Float('HK')
    location_id = fields.Many2one('stock.location', string='From')
    product_qty = fields.Float('To Consume')
    reserved = fields.Float('Reserved')
    consume = fields.Float('Consume')
    breakdown_id = fields.Many2one('mrp.breakdown', string='Breakdown')

class MrpBreakdown(models.Model):
    _name = 'mrp.breakdown'
    _description = 'Mrp Breakdown'
    _inherit = 'mail.thread'

    name = fields.Char('Name',tracking=True,default=lambda x: _('New'))
    product_id = fields.Many2one('product.template', string='Product',tracking=True)
    bom_id = fields.Many2one('mrp.bom', string='Bill of Material',tracking=True, help="Bill of Materials allow you to define the list of required components to make a finished product.")
    customer_id = fields.Many2one('res.partner', string='Customer',tracking=True)
    purchase_id = fields.Many2one('purchase.order', string='Purchase',tracking=True)
    product_qty = fields.Float('Quantity',default=1.0, required=True)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',related="product_id.uom_id")
    variant_detail_ids = fields.One2many('variant.detail', 'breakdown_id', string='Variant Detail')
    breakdown_line_ids = fields.One2many('mrp.breakdown.line', 'breakdown_id', string='Details')
    component_ids = fields.One2many('component.breakdown', 'breakdown_id', string='Component')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',)

    def break_down_to_mo(self):
        for i in self:
            if i.product_id.product_variant_ids:
                for l in i.product_id.product_variant_ids:
                    mo_temp = self.env["mrp.production"].create({
                        "name": ('New'),
                        })

    # product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    # picking_type_id = fields.Many2one(
    #     'stock.picking.type', 'Operation Type',
    #     domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
    #     default=_get_default_picking_type, required=True, check_company=True)


