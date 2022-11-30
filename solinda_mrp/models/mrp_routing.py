from email.policy import default
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'

    @api.depends('shrinkage')
    def _compute_shrinkage(self):
        for line in self:
            if line.shrinkage:
                res = line.hk - line.hk * line.shrinkage / 100
                line.shkg = res
            else:
                line.shkg = 0

    @api.depends('qty','cost_service', 'hk', 'shkg','shrinkage')
    def _compute_total_services(self):
        for line in self:
            if line.shrinkage:
                line.total_services = line.cost_service * line.shkg
            else:
                line.total_services = line.cost_service * line.hk

    qty = fields.Float(string='Qty', related='bom_id.product_qty', store=True)
    product_service_id = fields.Many2one('product.product', related='workcenter_id.product_service_id')
    # seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors', depends_context=('company',), help="Define vendor pricelists.")
    supplier = fields.Many2one('res.partner',string='Supplier')
    cost_service = fields.Float(string="Cost")
    fabric_id = fields.Many2one(comodel_name='mrp.bom.line',string='Fabric')
    hk = fields.Float(string='HK', related='fabric_id.product_qty')
    time_cycle_manual = fields.Float(string='Qty', related='bom_id.product_qty', store=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Service', required=True, check_company=True)
    color_id = fields.Many2one(comodel_name='product.attribute.value', string='Color', domain="[('attribute_id.name','=', 'COLOR')]")
    shrinkage = fields.Float(string='Shkg(%)', default=0.0)
    shkg = fields.Float(string='Shkg', compute = _compute_shrinkage, store=True)
    total_services = fields.Float(string="Total Services", compute=_compute_total_services, store=True)

    @api.onchange('workcenter_id','supplier')
    def _onchange_workcenter_idsupplier(self):
        active_ids = self._context.get("active_ids")
        bom = self.env['mrp.bom'].browse(active_ids)
        for i in self:
            if i.workcenter_id and i.supplier:
                if i.workcenter_id.product_service_id:
                    supplierinfo = self.env["product.supplierinfo"].search(
                        [("name", "=", i.supplier.id), ("product_tmpl_id", "=", i.product_service_id.product_tmpl_id.id)]
                    )
                    if supplierinfo:
                        i.cost_service = supplierinfo.price
                    else:
                        i.cost_service = 0
                else:
                    raise ValidationError("Product is not defined in master workcenter!")
            else:
                i.cost_service = 0


# class SupplierInfo(models.Model):
#     _inherit = 'product.supplierinfo'

#     workcenter_ids = fields.One2many('mrp.routing.workcenter', 'name', string='Work Center')
 