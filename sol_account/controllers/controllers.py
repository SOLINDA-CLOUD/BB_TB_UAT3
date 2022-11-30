# -*- coding: utf-8 -*-
# from odoo import http


# class SolAccount(http.Controller):
#     @http.route('/sol_account/sol_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_account/sol_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_account.listing', {
#             'root': '/sol_account/sol_account',
#             'objects': http.request.env['sol_account.sol_account'].search([]),
#         })

#     @http.route('/sol_account/sol_account/objects/<model("sol_account.sol_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_account.object', {
#             'object': obj
#         })
