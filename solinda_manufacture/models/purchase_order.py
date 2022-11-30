from odoo import _, api, fields, models
from datetime import date,datetime
from odoo.exceptions import ValidationError

class TempProductMo(models.Model):
    _name = 'temp.product.mo'
    _description = 'Temp Product Mo'
    
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    product_qty = fields.Float('Quantity')
    purchase_id = fields.Many2one('purchase.order', string='Purchase')
 
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    temp_prodmo_ids = fields.One2many('temp.product.mo', 'purchase_id', string='Temp Product MO')
    breakdown_id = fields.Many2one('mrp.breakdown', string='Breakdown')
    mrp_id = fields.Many2one('mrp.production', string='MO',copy=False)
    mrp_ids = fields.Many2many('mrp.production', string='MO',copy=False)
    mrp_count = fields.Integer('Mrp Count',compute="_compute_mrp_count")

    @api.depends('mrp_ids')
    def _compute_mrp_count(self):
        for i in self:
            i.mrp_count = len(i.mrp_ids.ids)

    @api.onchange('order_line.product_id')
    def _onchange_order_line_product_id(self):
        temp2 = []
        for i in self:
            # temp = i.order_line.mapped('product_id.product_tmpl_id'):
            for l in i.order_line:
                if l.product_id.product_tmpl_id.product_variant_count >0:
                    temp2.append((0,0,{'product_tmpl_id':l.product_tmpl_id.id,'product_qty':l.product_qty}))
            i.temp_prodmo_ids = [(5,0,0)]
            i.write({'temp_prodmo_ids':temp2})

    def show_mrp_prod(self):
        if self.mrp_count == 1:
            return {
                'name': _("Manufacturing Order"),
                'view_mode': 'form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id':self.mrp_id.id,
                'domain': [('id', 'in', self.mrp_ids.ids)],
                'context': {'create': False}
            }
        else:
            return {
                'name': _("Manufacturing Order"),
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'domain': [('id', 'in', self.mrp_ids.ids)],
                'context': {'create': False}
            }
    
    @api.model
    def _get_default_picking_type(self):
        company = self.env["res.company"].search([('is_manufacturing', '=', True)],limit=1)
        company_id = self.env.context.get('default_company_id', company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id

    def get_location(self,product):
        self = self.sudo()
        company = self.env["res.company"].search([('is_manufacturing', '=', True)],limit=1)

        location_by_company = self.env['stock.location'].read_group([
            ('company_id', 'in', company.ids),
            ('usage', '=', 'production')
        ], ['company_id', 'ids:array_agg(id)'], ['company_id'])
        location_by_company = {lbc['company_id'][0]: lbc['ids'] for lbc in location_by_company}
        if product:
            location = product.with_company(company).property_stock_production
        else:
            location = location_by_company.get(company.id)[0]
        return location


    def create_mo_production(self):
        mrp,mo_line,by_prod_temp,update = [],[],[],[]
        BoM,location = False,False
        company = self.env["res.company"].search([('is_manufacturing', '=', True)],limit=1)
        company_bb = self.env["res.company"].search([('is_manufacturing', '=', False)],limit=1)
        if not company:
            raise ValidationError("Company for manufacture is not defined")
        if not company_bb:
            raise ValidationError("Company for SO is not defined")
        self = self.sudo()
        for data in self.order_line:
            update.append([0,0,{
					'product_id' : data.product_id.id,
					'name' : data.name,
					'product_uom_qty' : data.product_qty,
					'price_unit' : data.price_unit,
					'price_subtotal' : data.price_subtotal,
			}])
        so = self.env['sale.order'].create({
            'partner_id': company_bb.partner_id.id,
            'company_id': company.id,
            'order_line': update,
            # 'source': self.id,
            })
        for i in self:
            if i.mrp_count > 0:
                return i.show_mrp_prod()
            else:
                prod_template = i.order_line.mapped('product_id.product_tmpl_id')
            
                for pt in prod_template:
                    
                    header_product = i.order_line.filtered(lambda x: x.product_id.detailed_type in ['consu','product'] and x.product_id.product_tmpl_id.id == pt.id)[0]
                    prodpo_line = i.order_line.filtered(lambda x: x.product_id.detailed_type in ['consu','product']  and x.product_id.product_tmpl_id.id == pt.id)
                    by_prod_temp = []
                    for o in prodpo_line:
                        by_prod_temp.append((0,0, {
                                'product_id': o.product_id.id,
                                'product_uom_qty': o.product_qty,
                                'product_uom_id': o.product_uom.id,
                                'fabric_por_id': o.fabric_por.id,
                                'lining_por_id': o.lining_por.id,
                                'colour': o.colour,
                                'size': o.size,
                        })) 

                    for l in header_product:
                        if l.product_id:
                            location = i.get_location(l.product_id)
                            if l.product_id.bom_count > 0:
                                BoM = self.env["mrp.bom"].search([('product_tmpl_id', '=', l.product_id.product_tmpl_id.id),('is_final', '=', True)])
                                if not BoM:
                                    statement = "BoM final is not defined in product %s.\nPlease choose the final BoM first!" % l.product_id.product_tmpl_id.name
                                    raise ValidationError(statement)
                                if not BoM.picking_type_id:
                                    statement = "BoM Operation is not defined in product %s.\nPlease choose the operation first!" % l.product_id.product_tmpl_id.name
                                    raise ValidationError(statement)
                                if len(BoM) > 1:
                                    raise ValidationError("BoM final more than 1!")
                            else:
                                statement = "There is no BoM in product %s!" % l.product_id.product_tmpl_id.name
                                raise ValidationError(statement)
                            mp = self.env["mrp.production"].create({
                                'name': _('New'),
                                'product_id': l.product_id.id,
                                'product_qty': l.product_qty,
                                'product_uom_id':l.product_uom.id,
                                'bom_id':BoM.id,
                                'date_planned_start':datetime.now(),
                                'user_id': i.env.user.id,
                                'company_id': company.id,
                                'purchase_id':i.id,
                                'sales_order_id': so.id,
                                'picking_type_id':BoM.picking_type_id.id,
                                'location_src_id':BoM.picking_type_id.default_location_src_id.id,
                                'location_dest_id':BoM.picking_type_id.default_location_dest_id.id,
                                'production_location_id':location.id
                                })
                               
                            if mp:
                                # mp.move_raw_ids = [(2, move.id) for move in mp.move_raw_ids.filtered(lambda m: m.bom_line_id)]
                                mrp.append(mp.id)
                                for j in i.order_line:
                                    if j.product_id:
                                        mo_line.append((0,0, {
                                            'name': _('New'),
                                            'product_id': j.product_id.id,
                                            'location_dest_id': mp.location_dest_id.id,
                                            'location_id': location.id,
                                            'product_uom_qty': j.product_qty,
                                            'product_uom': j.product_id.uom_id.id,
                                        }))
                                mp.bom_id = BoM.id
                                list_move_raw = [(4, move.id) for move in mp.move_raw_ids.filtered(lambda m: not m.bom_line_id)]
                                moves_raw_values = mp._get_moves_raw_values()
                                move_raw_dict = {move.bom_line_id.id: move for move in mp.move_raw_ids.filtered(lambda m: m.bom_line_id)}

                                for move_raw_values in moves_raw_values:
                                    if move_raw_values['bom_line_id'] in move_raw_dict:
                                        # update existing entries
                                        list_move_raw += [(1, move_raw_dict[move_raw_values['bom_line_id']].id, move_raw_values)]
                                    else:
                                        # add new entries
                                        list_move_raw += [(0, 0, move_raw_values)]
                                mp.move_raw_ids = list_move_raw
                                mp._onchange_workorder_ids()
                                mp.update({'move_byproduct_ids':mo_line,'by_product_ids':by_prod_temp})
                i.write({'mrp_ids' : [(6,0,mrp)],'mrp_id':mp.id})
                return i.show_mrp_prod()

    def create_mrp_production(self):
        mrp = []
        BoM = False
        self = self.sudo()
        for i in self:
            if i.mrp_count > 0:
                return i.show_mrp_prod()
            else:
                company = self.env["res.company"].search([('is_manufacturing', '=', True)],limit=1)
                if not company:
                    raise ValidationError("Company for manufacture is not defined")
                for l in i.order_line:
                    if l.product_id:
                        if l.product_id.bom_count > 0:
                            BoM = self.env["mrp.bom"].search([('product_id', '=', l.product_id.id)],order = 'retail_price desc',limit=1).id
                        mp = self.env["mrp.production"].create({
                            'name': _('New'),
                            'product_id': l.product_id.id,
                            'product_qty': l.product_qty,
                            'product_uom_id':l.product_uom.id,
                            'bom_id':BoM,
                            'date_planned_start':datetime.now(),
                            'user_id': i.env.user.id,
                            'company_id': company.id,
                            'purchase_id':i.id,
                        
                            })
                        if mp:
                            mrp.append(mp.id)
                i.write({'mrp_ids' : [(6,0,mrp)]})
                return i.show_mrp_prod()
    

    def create_mrp_breakdown(self):
        self = self.sudo()
        breakdown = ''
        for i in self:
            for l in i.temp_prodmo_ids:
                breakdown = self.env["mrp.breakdown"].create({
                            # 'name': ,
                            'product_id': l.id,
                            'customer_id': i.partner_id.id,
                            'purchase_id': i.id,
                            'uom_id':l.product_tmpl_id.uom_id.id,
                            'product_qty':l.product_qty
                        })
                if breakdown:
                    i.breakdown_id = breakdown.id
                    return {
                        'name': _("Manufacturing"),
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_model': 'temp.product.mo',
                        'type': 'ir.actions.act_window',
                        'res_id': breakdown.id,
                    } 