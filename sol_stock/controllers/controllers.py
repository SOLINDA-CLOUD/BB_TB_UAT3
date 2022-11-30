# -*- coding: utf-8 -*-
# from odoo import http


# class SolStock(http.Controller):
#     @http.route('/sol_stock/sol_stock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_stock/sol_stock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_stock.listing', {
#             'root': '/sol_stock/sol_stock',
#             'objects': http.request.env['sol_stock.sol_stock'].search([]),
#         })

#     @http.route('/sol_stock/sol_stock/objects/<model("sol_stock.sol_stock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_stock.object', {
#             'object': obj
#         })
