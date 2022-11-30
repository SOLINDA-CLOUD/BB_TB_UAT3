# -*- coding: utf-8 -*-
# from odoo import http


# class SolPurchase(http.Controller):
#     @http.route('/sol_purchase/sol_purchase', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_purchase/sol_purchase/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_purchase.listing', {
#             'root': '/sol_purchase/sol_purchase',
#             'objects': http.request.env['sol_purchase.sol_purchase'].search([]),
#         })

#     @http.route('/sol_purchase/sol_purchase/objects/<model("sol_purchase.sol_purchase"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_purchase.object', {
#             'object': obj
#         })
