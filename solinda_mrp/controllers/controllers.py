# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaMrp(http.Controller):
#     @http.route('/solinda_mrp/solinda_mrp', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_mrp/solinda_mrp/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_mrp.listing', {
#             'root': '/solinda_mrp/solinda_mrp',
#             'objects': http.request.env['solinda_mrp.solinda_mrp'].search([]),
#         })

#     @http.route('/solinda_mrp/solinda_mrp/objects/<model("solinda_mrp.solinda_mrp"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_mrp.object', {
#             'object': obj
#         })
