from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import ValidationError

_STATES = [
  ("draft", "Draft"),
  ("order", "Order"),
  ("unorder", "Unorder"),
]

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )

    name = fields.Char(
        required=False,
        default='New',
        index=True,
        readonly=True,
        string='Trans No.'
    )

    trans_date = fields.Datetime(
        string='Transaction Date',
        default=fields.Datetime.now,
        index=True,
        required=True,
        )

    parent_pps = fields.Char(string='Parent PPS')

    @api.model
    def create(self, vals):
        self = self.sudo()
        iterate = self.env['ir.sequence'].next_by_code('mrp.bom')
        if iterate:
            vals['name'] = iterate
        else:
            vals['name'] = 'New'
        return super(MrpBom, self).create(vals)

    @api.depends('over_packaging', 'bom_line_ids.total_material', 'operation_ids.total_services')
    def _compute_total_cost(self):
        for line in self:
            total_material = 0
            total_operation = 0
            total = 0
            for bom in line.bom_line_ids:
                total_material += bom.total_material
            for op in line.operation_ids:
                total_operation += op.total_services
            total = total_operation + total_material + line.over_packaging
            line.total_cost = total

    @api.depends('total_cost', 'margin')
    def _compute_suggest_price(self):
        for line in self:
            line.suggest_price = line.total_cost + (line.total_cost * line.margin)

    @api.depends('total_cost', 'margin_2')
    def _compute_suggest_price_2(self):
        for line in self:
            line.suggest_price_2 = line.total_cost + (line.total_cost * line.margin_2)
    
    @api.depends('total_cost', 'margin_3')
    def _compute_suggest_price_3(self):
        for line in self:
            line.suggest_price_3 = line.total_cost + (line.total_cost * line.margin_3)

    # @api.onchange('total_cost', 'margin')
    # def total_suggest_price(self):
    #     for line in self:
    #         line.suggest_price = line.total_cost + (line.total_cost * line.margin)

    # @api.onchange('total_cost', 'margin_2')
    # def total_suggest_price_2(self):
    #     for line in self:
    #         line.suggest_price_2 = line.total_cost + (line.total_cost * line.margin_2)
    
    # @api.onchange('total_cost', 'margin_3')
    # def total_suggest_price_3(self):
    #     for line in self:
    #         line.suggest_price_3 = line.total_cost + (line.total_cost * line.margin_3)

    def order(self):
        return self.write({"state":"order"})
    
    def unorder(self):
        return self.write({"state":"unorder"})
    
    code = fields.Char('Child PPS')
    over_packaging = fields.Float(string='Over & Packaging', default=0.00)
    customer = fields.Many2one(comodel_name='res.partner', string='Customer')
    categ_id = fields.Many2one('product.category', related='product_tmpl_id.categ_id', string='Group')
    retail_price = fields.Float(related='product_tmpl_id.list_price', string='Retail Price')
    is_final = fields.Boolean('Final')
    total_cost = fields.Float(string="Total Cost", compute=_compute_total_cost)
    margin = fields.Float(string="Margin 1")
    margin_2 = fields.Float(string="Margin 2")
    margin_3 = fields.Float(string="Margin 3")
    suggest_price = fields.Float(string="Suggest Price", compute=_compute_suggest_price)
    suggest_price_2 = fields.Float(string="Suggest Price 2", compute=_compute_suggest_price_2)
    suggest_price_3 = fields.Float(string="Suggest Price 3", compute=_compute_suggest_price_3)


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.depends('product_qty', 'cost')
    def _compute_total_material(self):
        for line in self:
            line.total_material = line.cost * line.product_qty

    @api.depends('product_id')
    def _onchange_color_size(self):
        for i in self:
            c,s = '',''
            if i.product_id.product_template_variant_value_ids:
                i.color = i.product_id.product_template_variant_value_ids
                list_size = ['SIZE:','SIZES:','UKURAN:']
                list_color = ['COLOR:','COLOUR:','COLOURS:','COLORS:','WARNA:','CORAK:']
                for v in i.product_id.product_template_variant_value_ids:
                    if any(v.display_name.upper().startswith(word) for word in list_color):
                        c += '('+v.name+')'
                    elif any(v.display_name.upper().startswith(word) for word in list_size):
                        s += '('+v.name+')'
                    else:
                        c += ''
                        s += ''
            else:
                c = ''
                s = ''
            i.color = c
            i.sizes = s

    supplier = fields.Many2one('res.partner',string='Supplier')
    color = fields.Char('Color',compute="_onchange_color_size")
    sizes = fields.Char('Sizes',compute="_onchange_color_size")
    ratio = fields.Float(string='Ratio', default=1.00)
    cost = fields.Float(string="Cost", related='product_id.standard_price')
    total_material = fields.Float(string="Total Material", compute=_compute_total_material)

class Sizes(models.Model):
    _name = 'sizes'
    _description = 'Sizes'

    name = fields.Char(string='Name')

class DptColor(models.Model):
    _name = 'dpt.color'
    _description = 'DPT Color'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')

    @api.constrains('name')
    def _check_code_unique(self):
        if self.name:
            ref_counts = self.search_count(
                [('name', '=', self.name), ('id', '!=', self.id)])
            if ref_counts > 0:
                raise ValidationError("Color already exists!")
        else:
            return

    @api.constrains('code')
    def _check_code_unique(self):
        if self.code:
            ref_counts = self.search_count(
                [('code', '=', self.code), ('id', '!=', self.id)])
            if ref_counts > 0:
                raise ValidationError("Code already exists!")
        else:
            return
