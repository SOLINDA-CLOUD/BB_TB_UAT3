from odoo import models, fields, api


class SalesOrder(models.Model):
  _inherit = 'sale.order'

  # def default_warehouse(self):
  #   return self.env['stock.warehouse'].search(['|', ('name', '=', 'FINISH GOODS FROM SEWING SUPPLIER'), ('company_id')], limit=1).id

  po_number = fields.Char('PO No')
  source = fields.Many2one('purchase.order', string='Source Document PO')
  so_number = fields.Char('SO No')
  prepared = fields.Char(string='Prepared By')
  ordered = fields.Many2one('res.users', string='Ordered By')
  approved = fields.Many2one('res.users', string='Approved By')
  # warehouse_id = fields.Many2one(
  #   'stock.warehouse', string='Warehouse',
  #   required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
  #   default=default_warehouse, check_company=True)

  @api.model
  def create(self, vals):
    res = super(SalesOrder, self).create(vals)
    res.name = self.env["ir.sequence"].next_by_code("sale.order.seq")
    return res

class SaleOrderLine(models.Model):
  _inherit = 'sale.order.line'

  # color = fields.Many2one('product.product', string="Size and Color")
  colour = fields.Char('Color',compute="_onchange_color_size")
  size = fields.Char('Size',compute="_onchange_color_size")
  color = fields.Char('Color')
  # size = fields.Char('Size')

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