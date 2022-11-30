from odoo import fields, api, models,_
from datetime import datetime, date
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    supplier = fields.Many2one(comodel_name='res.partner',related="bom_line_id.supplier", string='Supplier')
    # payment = fields.Many2one(comodel_name='account.payment.method', related='supplier.property_payment_method_id')
    color = fields.Many2one(comodel_name='dpt.color', string='Color')
    service = fields.Char(string='Fabric', default='FABRIC', readonly=True)
    hk = fields.Float(string='HK', related='bom_line_id.product_qty', store=True)
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
    total_buy = fields.Float(string="Total Buy")
    # total_mtr = fields.Float(string="Total Mtr")
    total_cost = fields.Float(string="Total Cost", compute = "_compute_total_cost", store=True)
 

    def show_receive_po(self):
        self.purchase_id.action_view_picking()
        return self.purchase_id.action_view_picking()

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
        self = self.sudo()
        for i in self:
            raw_po_line = []
            total_quant = i.product_qty
            if not i.supplier:
                raise ValidationError("Please input the supplier first")
            po = i.env['purchase.order'].create({'partner_id': i.supplier.id,'state': 'draft','date_approve': datetime.now()})
            picking = po._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
            # picking = i.raw_material_production_id.picking_type_id.id
            # picking = i.env['stock.picking.type'].search([('barcode', '=', 'WHFG-RECEIPTS')],limit=1)
            if not picking:
                raise ValidationError("WHFG-RECEIPTS is not defined!")
            if po:
                i.purchase_id = po.id
            raw_po_line.append((0,0, {
                'product_id': i.product_id.id,
                # 'fabric': i.fabric_id.product_id.name,
                # 'lining':'',
                # 'color':'',
                'product_qty': total_quant,
            }))           
            po.update({"order_line": raw_po_line,"picking_type_id":picking})
            po.button_confirm()
            for picking in po.picking_ids:
                for move in picking.move_ids_without_package:
                    move.raw_material_production_id = False
            
            return i.show_po()

    @api.depends('product_id.standard_price', 'product_uom_qty', 'hk', 'total_buy')
    def _compute_total_cost(self):
        for line in self:
            if line.total_buy:
                line.total_cost = line.product_id.standard_price * line.total_buy
            else:
                line.total_cost = line.product_id.standard_price * line.product_uom_qty * line.hk