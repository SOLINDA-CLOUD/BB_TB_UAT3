from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class MrpBomTender(models.Model):
    _inherit = 'mrp.bom'

    tender_id = fields.Many2one('tender.bom', string='Tender')    

    def order(self):
        for i in self:
            if i.tender_id:
                for l in i.tender_id.bom_ids:
                    if l.id != i.id:
                        l.state = 'unorder'
                    else:
                        i.tender_id.deal_bom_id = i.id
                        l.state = 'order'
                        l.is_final = True
                i.tender_id.state = 'vote'
            else:
                raise ValidationError("Transaction not succed!\nThis BoM is not include in tender.")
    
    def unorder(self):
        return self.write({"state":"unorder"})

class TenderBom(models.Model):
    _name = 'tender.bom'

    name = fields.Char('Name')
    state = fields.Selection([('draft', 'Draft'),('vote', 'Voted/done')], string='State',default='draft')
    date = fields.Date('Created Date',default=fields.date.today())
    end_tender = fields.Date('End Tender')
    bom_ids = fields.One2many('mrp.bom', 'tender_id', string='BoM')
    count_bom = fields.Integer(compute='_compute_count_bom', string='Count Bom')
    product_id = fields.Many2one('product.product', string='Product Variant',required=False)
    product_tmpl_id = fields.Many2one('product.template', string='Product')
    deal_bom_id = fields.Many2one('mrp.bom', string='Deal Pre-Production Sample')

    def new_bom(self):
        for i in self:
            bom = i.env['mrp.bom'].sudo().create({
                "name" : 'New',
                "tender_id" : i.id,
                "company_id" : i.env.company.id,
                "product_tmpl_id" : i.product_tmpl_id.id,
                "code" : i.name,
                "state" : 'draft',
                "parent_pps": i.name,
            })      
            if bom:
                return {
                'name': _("Pre-Production Sample"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'mrp.bom',
                'type': 'ir.actions.act_window',
                'domain': [('tender_id','=',self.id)],
                'context': {'default_company_id': self.env.company.id,'default_tender_id':self.id},
                'res_id':bom.id
            } 

    def set_to_draft(self):
        for b in self.bom_ids:
            b.state = 'draft'
            b.is_final = False
        self.write({"state":"draft"})     

    def final_bom(self):
        return {
                'name': _("Pre-Production Sample"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'mrp.bom',
                'type': 'ir.actions.act_window',
                'res_id':self.deal_bom_id.id,
                'context': {'create': False},
            } 

    @api.depends('bom_ids')
    def _compute_count_bom(self):
        self.count_bom = len(self.bom_ids.ids)

    def show_bom(self):
        if self.count_bom < 1:
            raise ValidationError("Pre-Production Sample is not defined!\nPlease create Pre-Production Sample first")
        return {
                'name': _("Pre-Production Sample"),
                'view_mode': 'tree,form',
                'res_model': 'mrp.bom',
                'type': 'ir.actions.act_window',
                'domain': [('tender_id','=',self.id)],
                'context': {'default_company_id': self.env.company.id,'default_tender_id':self.id},
            } 
