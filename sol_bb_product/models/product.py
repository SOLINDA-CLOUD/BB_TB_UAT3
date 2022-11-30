from odoo import fields, api, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    # def _compute_standard_price(self):
    #     # Depends on force_company context because standard_price is company_dependent
    #     # on the product_product
    #     # unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
    #     # for template in unique_variants:
    #     #     template.standard_price = template.product_variant_ids.standard_price
    #     # for template in (self - unique_variants):
    #     #     template.standard_price = 1
    #     return self.standard_price

    # def _set_standard_price(self):
    #     for template in self:
    #         if len(template.product_variant_ids) > 1:
    #             template.product_variant_ids.standard_price = template.standard_price

    order_notes = fields.Html(string='Order Notes')
    collection_product = fields.Many2one('product.collections', string='Collection')
    launch_date = fields.Date(string='Launch Date')
    class_product = fields.Many2one('class.product', string='Class')
    default_code = fields.Char(string='Internal Reference', related='product_tmpl_id.default_code', store=True)
    consumption = fields.Float(string="Consumption")
    fabric_width = fields.Float(string="Fabric Width")
    category = fields.Char(related='categ_id.name', string='Category')
    standard_price = fields.Float(related='product_tmpl_id.standard_price')
    product_template_variant_value_ids = fields.Many2many('product.template.attribute.value', relation='product_variant_combination', domain=[('attribute_line_id.value_count', '>=', 1)], string="Variant Values", ondelete='restrict')



class ProductCollections(models.Model):
    _name = 'product.collections'
    _description = 'Product Collections'

    name = fields.Char(string='Name')

class ClassProduct(models.Model):
    _name = 'class.product'
    _description = 'Class'

    name = fields.Char(string="Class")