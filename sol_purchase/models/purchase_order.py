from odoo import _, fields, api, models

class BuyerComp(models.Model):
  _name = 'buyer.comp'
  name = fields.Char('buyer')

class AttComp(models.Model):
  _name = 'att.comp'
  name = fields.Char('attention')

class LabelComp(models.Model):
  _name = 'label.comp'
  name = fields.Char('Label')

class ProductWorkorder(models.Model):
  _name = 'product.workorder'

  purchase_pw = fields.Many2one('purchase.order', string='PO')
  name = fields.Many2one('product.product', string='Style Name')
  fabric = fields.Many2one('product.product', string='Fabric')
  lining = fields.Many2one('product.product', string='Lining')
  color = fields.Char(string='Color')
  size = fields.Char(string='Size')
  image = fields.Image(string='Image')
  product_qty = fields.Float(string='Qty')
  price_unit = fields.Float(string='Price Unit')
  sample_comment = fields.Html(string='Sample Comment')

class PurchaseOrder(models.Model):
  _inherit = 'purchase.order'

  attention = fields.Many2one(comodel_name='att.comp', string='Attention')
  sub_suplier = fields.Many2many('res.partner.category', string='Division')
  brand = fields.Many2one('product.brand', string='Brand')
  buyer = fields.Many2one(comodel_name='buyer.comp',string='Buyer')
  sample_order_no = fields.Char(string='Order No')
  supplier_po = fields.Char('Supplier PO')
  po = fields.Char('PO')
  ordering_date = fields.Date(string='Delivery Date', states={'purchase': [('readonly', True)]})
  delivery_date = fields.Date(states={'purchase': [('readonly', True)]})
  pw_ids = fields.One2many(comodel_name='product.workorder', inverse_name='purchase_pw', string='Product from MO')
  product_qty = fields.Float(string='Quantity', default=1)

  ##SIGNATURE##
  prepared = fields.Many2one('res.users', string='Prepared By')
  ordered = fields.Many2one('res.users', string='Ordered By')
  approved = fields.Many2one('res.users', string='Approved By')
  
  @api.model
  def create(self, vals):
      res = super(PurchaseOrder, self).create(vals)
      # res.name = self.env["ir.sequence"].next_by_code("purchase.order.seq")
      if not vals.get("name") or vals.get("name") == "New":
          vals["name"] = (
              self.env["ir.sequence"].next_by_code("purchase.order.seq") or "New"
          )
      return res

class PurchaseOrderLine(models.Model):
  _inherit = 'purchase.order.line'

  product_id = fields.Many2one(string='Style Name')
  image = fields.Image(string='Image')
  fabric_por = fields.Many2one('product.product', string='Fabric')
  lining_por = fields.Many2one('product.product', string='Lining')
  color = fields.Many2many('product.template.attribute.value', string="Size and Color")
  colour = fields.Char('Color',compute="_onchange_color_size")
  size = fields.Char('Size',compute="_onchange_color_size")
  label = fields.Many2one(comodel_name='label.comp', string='Label')
  prod_comm = fields.Html(string='Comment')
  comment_bool = fields.Boolean(default=False)

  @api.onchange('product_id')
  def _onchange_image(self):
    if self.product_id:
      image = ''
      if self.product_id.image_1920:
        self.image = self.product_id.image_1920
      return image

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
      i.colour = c
      i.size = s

            