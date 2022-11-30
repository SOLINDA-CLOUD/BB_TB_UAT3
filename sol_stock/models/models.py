
from odoo import models, fields, api
import datetime

class StockPickingType(models.Model):
  _inherit = 'stock.picking.type'

  mandatory_source = fields.Boolean('Required Source Documents', default=False)

class StockPicking(models.Model):
  _inherit = 'stock.picking'

  origin_pr = fields.Many2one('purchase.request', 'Source Document', index=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, help="Reference of the document")
  mandatory_source = fields.Boolean(related='picking_type_id.mandatory_source', string='Required Source Documents', readonly=True, related_sudo=False)
  # analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')

class StockMove(models.Model):
  _inherit = 'stock.move'

  fabric_width = fields.Float(string="Fabric Width", related='product_id.fabric_width')
  price = fields.Float(string="Price", related='product_id.standard_price')
  image = fields.Image(string='Image')

  @api.onchange('product_id')
  def _onchange_image(self):
      if self.product_id:
          self.image = ''
          if self.product_id.image_1920:
              self.image = self.product_id.image_1920
          self.image = self.image
