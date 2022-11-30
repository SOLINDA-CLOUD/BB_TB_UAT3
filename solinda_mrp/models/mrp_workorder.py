from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import formatLang, get_lang, format_amount

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    order_id = fields.Many2one(comodel_name='purchase.order',string='PO')
    supplier = fields.Many2one(comodel_name='res.partner',related="operation_id.supplier", string='Supplier')
    fabric_id = fields.Many2one(comodel_name='mrp.bom.line',string='Fabric', related='operation_id.fabric_id')
    hk = fields.Float(string='HK', related='operation_id.hk', store=True)
    color_id = fields.Many2one(comodel_name='product.attribute.value', string='Color', related='operation_id.color_id')
    shrinkage = fields.Float(string='Shkg(%)', default=0.0)
    duration_expected = fields.Float(
        'Expected Duration',
        digits=(16, 2),
        default=1.0,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Expected duration (in minutes)")
    
    qty_production = fields.Float(string="Qty", related='production_id.product_qty', store=True)
    in_date = fields.Date('In Date')
    out_date = fields.Date('Out Date')
    picking_ids = fields.Many2many('stock.picking', string='Receive',related="order_id.picking_ids")
    total_dyeing = fields.Float(string='Total Dyeing')
    # total_mtr_dye = fields.Float(string='Total Mtr')
    total_cost = fields.Float(string="Total Cost", compute="_compute_total_cost", store=True)

    @api.depends('total_dyeing', 'hk', 'qty_production', 'workcenter_id.costs_hour')
    def _compute_total_cost(self):
        for line in self:
            if line.total_dyeing:
                line.total_cost = line.total_dyeing * line.workcenter_id.costs_hour
            else:
                line.total_cost = line.hk * line.qty_production * line.workcenter_id.costs_hour

    def show_receive_po(self):
        self.order_id.action_view_picking()
        return self.order_id.action_view_picking()

    def show_po(self):
        if not self.order_id:
            raise ValidationError("PO is not defined!\nPlease create PO first")
        return {
                'name': _("Purchase Order"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                # 'target': 'new',
                'res_id': self.order_id.id,
            } 

    def create_po(self):
        self = self.sudo()
        for i in self:
            raw_po_line = []
            total_quant = sum(i.production_id.purchase_id.order_line.mapped('product_qty'))
            i.button_start()
            if not i.supplier:
                raise ValidationError("Please input the supplier first")
            po = i.env['purchase.order'].create({'partner_id': i.supplier.id,'state': 'draft','date_approve': datetime.now()})
            if po:
                i.order_id = po.id
            if not i.workcenter_id.product_service_id:
                raise ValidationError("Default product in Workcenter is not defined!\nPlease input product in workcenter as default when create PO from Work Order")
            raw_po_line.append((0,0, {
                'product_id': i.workcenter_id.product_service_id.id,
                'name': i.workcenter_id.product_service_id.name,
                # 'fabric': i.fabric_id.product_id.name,
                # 'lining':'',
                # 'color':'',
                'product_qty': total_quant,
            }))           
            po.update({"order_line": raw_po_line})
            for pol in po.order_line:
                product_lang = pol.product_id.with_context(
                    lang=get_lang(pol.env, pol.partner_id.lang).code,
                    partner_id=pol.partner_id.id,
                    company_id=pol.company_id.id,
                )
                pol.name = pol._get_product_purchase_description(product_lang)
            po.button_confirm()
            i.show_po()
            

    def create_po_action(self):
        self.ensure_one()
        if any(not time.date_end for time in self.time_ids.filtered(lambda t: t.user_id.id == self.env.user.id)):
            return True
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True
        
        if self.product_tracking == 'serial':
            self.qty_producing = 1.0
        else:
            self.qty_producing = self.qty_remaining
        self.env['mrp.workcenter.productivity'].create(
            self._prepare_timeline_vals(self.duration, datetime.now())
        )
        if self.production_id.state != 'progress':
            self.production_id.write({
                'date_start': datetime.now(),
            })
        if self.state == 'progress':
            return True
        
        start_date = datetime.now()

        if not self.supplier:
            raise ValidationError("Please Input Supplier first!")

        vals = {
            'state': 'progress',
            'date_start': start_date,
        }
        po = self.env['purchase.order'].create({
            'partner_id': self.supplier.id,
            'state': 'purchase',
            'date_approve': start_date,
        })

        if not self.workcenter_id.product_service_id:
            raise ValidationError("Product Service in this Workcenter hasn't been set")
        
        self.env['purchase.order.line'].create({
            'product_id': self.workcenter_id.product_service_id.id,
            'product_qty': self.qty_producing,
            'order_id': po.id,
        })
        vals['order_id'] = po.id
        if not self.leave_id:
            leave = self.env['resource.calendar.leaves'].create({
                'name': self.display_name,
                'calendar_id': self.workcenter_id.resource_calendar_id.id,
                'date_from': start_date,
                'date_to': start_date + relativedelta(minutes=self.duration_expected),
                'resource_id': self.workcenter_id.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            return self.write(vals)
        else:
            if self.date_planned_start > start_date:
                vals['date_planned_start'] = start_date
            if self.date_planned_finished and self.date_planned_finished < start_date:
                vals['date_planned_finished'] = start_date
            return self.with_context(bypass_duration_calculation=True).write(vals)
