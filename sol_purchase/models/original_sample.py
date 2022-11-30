from odoo import _, models, fields, api


_STATES = [
  ("draft", "Original Sample"),
  ("done", "Sample Master"),
]

class AttributeLine(models.Model):
  _name = 'attribute.line'
  _description = 'Attribute Line'
  
  # def _default_attribute(self):
  #   return self.env['product.attribute'].search([('name', '=', 'SIZE')], limit=1).id
  # @api.model
  # def default_attribute(self):
  #   updt_att = []
  #   res = self.env["product.attribute"].search([("name", "=", "SIZE")])
  #   for attribute in self:
  #     updt_att.update([
  #       4, attribute.id 
  #     ])
  #   return res

  attribute_id = fields.Many2one('product.attribute', string='Attribute')
  value_ids = fields.Many2many('product.attribute.value', string='Values', domain="[('attribute_id', '=', attribute_id)]", required=True)
  original_sample_id = fields.Many2one(comodel_name='original.sample', string='Form Attribute')


class OriginalSample(models.Model):
  _name = 'original.sample'
  _description = 'Original Sample Register'
  _order = "id desc"

  def default_get(self, fields):
    res = super(OriginalSample, self).default_get(fields)
    updt_att = []
    att = self.env["product.attribute"].search([('name', '=', 'SIZE')])
    for rec in att:
      line = (0,0,{
        'attribute_id': rec.id
      })
      updt_att.append(line)
    res.update({
      'line_attribute_ids': updt_att
    })
    return res

  def default_uom_id(self):
    return self.env['uom.uom'].search([('name', '=', 'Pcs')], limit=1).id

  state = fields.Selection(
    selection=_STATES,
    string="Status",
    index=True,
    tracking=True,
    required=True,
    copy=False,
    default="draft",
  )
  ref = fields.Char('Original Sample No.')
  name = fields.Char('Product Name')
  photo = fields.Image('Image')
  sample_origin = fields.Char('Sample Origin')
  date_in = fields.Date('Date In')
  date_out = fields.Date('Date Out')
  qty_in = fields.Integer('Quantity In')
  qty_out = fields.Integer('Quantity Out')
  balance = fields.Integer(string='Balance', compute='compute_sisa_stock')
  note = fields.Html('Note')
  department = fields.Many2one('product.category', string='Department / Category / Sub Category')
  currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.company.currency_id.id)
  original_price = fields.Monetary(store=True, string='Original Price')
  detailed_type = fields.Selection([('consu', 'Consumable'),('service', 'Service'),('product', 'Storable')], default='product')
  line_attribute_ids = fields.One2many(comodel_name='attribute.line', inverse_name='original_sample_id', string='Attribute')
  uom_id = fields.Many2one('uom.uom', string='UOM', default=default_uom_id)

  @api.model
  def create(self, vals):
    res = super(OriginalSample, self).create(vals)
    res.ref = self.env["ir.sequence"].next_by_code("original.sample.sequ")
    return res  

  def convert_master_product(self):
    update_attribute, updt_prline = [],[]
    for i in self.line_attribute_ids:
      update_attribute.append([0,0,{
        'attribute_id': i.attribute_id.id,
        'value_ids': i.value_ids.ids,
      }])
    pt = self.env['product.product'].create({
      'name': self.name,
      'categ_id': self.department.id,
      'image_1920': self.photo,
      'detailed_type': self.detailed_type,
      'uom_id': self.uom_id.id,
      'uom_po_id': self.uom_id.id,
      'from_origin': True,
      'no_origin': self.ref,
    })
    pt.update({
      'attribute_line_ids': update_attribute,
    })
    updt_prline.append([0,0,{
      'product_id': pt.id,
      'image': self.photo,
      'name': self.name,
      'department': self.department.id,
      'product_uom_id': pt.uom_po_id.id,
    }])
    self.env['purchase.request'].create({
      'name_source': self.name,
      'source': self.ref,
      'line_ids': updt_prline,
    })

    return self.write({"state": "done"})
  
  def compute_sisa_stock(self):
    for i in self:
      i.balance = i.qty_in - i.qty_out or 0
  
