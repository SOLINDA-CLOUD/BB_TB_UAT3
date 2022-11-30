from dataclasses import field
from odoo import fields, api, models

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    notes = fields.Text(string='Notes')