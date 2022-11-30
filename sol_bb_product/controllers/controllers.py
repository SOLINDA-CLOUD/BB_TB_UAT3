# -*- coding: utf-8 -*-
# from odoo import http


# class SolBbProduct(http.Controller):
#     @http.route('/sol_bb_product/sol_bb_product', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_bb_product/sol_bb_product/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_bb_product.listing', {
#             'root': '/sol_bb_product/sol_bb_product',
#             'objects': http.request.env['sol_bb_product.sol_bb_product'].search([]),
#         })

#     @http.route('/sol_bb_product/sol_bb_product/objects/<model("sol_bb_product.sol_bb_product"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_bb_product.object', {
#             'object': obj
#         })
