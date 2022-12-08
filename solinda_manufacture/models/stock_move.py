from odoo import _, api, fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def compute_mrp_workorders(self):
        for rec in self:
            workorder_list = []
            sql = '''SELECT w.id as workorder_id FROM mrp_workorder w WHERE w.production_id=%s'''% (rec.production_id.id)
            self.env.cr.execute(sql)
            workorder_ids = self.env.cr.dictfetchall()
            for w in workorder_ids:
                workorder_list.append((4, w['workorder_id'], None))
            rec.workorder_ids = workorder_list

    workorder_ids = fields.Many2many(comodel_name='mrp.workorder', string='Work Orders', compute='compute_mrp_workorders')

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.depends('product_uom_qty')
    def compute_qty_available(self):
        for rec in self:
            is_available = True
            if rec.product_uom_qty > rec.product_qty_available:
                is_available = False
            rec.is_available = is_available

    is_available = fields.Boolean('Is Available', compute='compute_qty_available', store=True)

    
    