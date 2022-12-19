from odoo import fields, api, models,_
from datetime import datetime, date
from odoo.exceptions import ValidationError

class StockMove(models.Model):
    _inherit = 'stock.move'

    
    