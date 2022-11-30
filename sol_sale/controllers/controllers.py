# -*- coding: utf-8 -*-
# from odoo import http


# class SolSale(http.Controller):
#     @http.route('/sol_sale/sol_sale', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_sale/sol_sale/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_sale.listing', {
#             'root': '/sol_sale/sol_sale',
#             'objects': http.request.env['sol_sale.sol_sale'].search([]),
#         })

#     @http.route('/sol_sale/sol_sale/objects/<model("sol_sale.sol_sale"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_sale.object', {
#             'object': obj
#         })
