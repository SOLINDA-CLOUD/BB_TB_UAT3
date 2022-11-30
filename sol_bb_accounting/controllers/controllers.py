# -*- coding: utf-8 -*-
# from odoo import http


# class SolBbAccounting(http.Controller):
#     @http.route('/sol_bb_accounting/sol_bb_accounting', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sol_bb_accounting/sol_bb_accounting/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sol_bb_accounting.listing', {
#             'root': '/sol_bb_accounting/sol_bb_accounting',
#             'objects': http.request.env['sol_bb_accounting.sol_bb_accounting'].search([]),
#         })

#     @http.route('/sol_bb_accounting/sol_bb_accounting/objects/<model("sol_bb_accounting.sol_bb_accounting"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sol_bb_accounting.object', {
#             'object': obj
#         })
