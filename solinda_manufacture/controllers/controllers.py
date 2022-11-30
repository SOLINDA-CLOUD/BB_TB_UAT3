# -*- coding: utf-8 -*-
# from odoo import http


# class SolindaManufacture(http.Controller):
#     @http.route('/solinda_manufacture/solinda_manufacture', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/solinda_manufacture/solinda_manufacture/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('solinda_manufacture.listing', {
#             'root': '/solinda_manufacture/solinda_manufacture',
#             'objects': http.request.env['solinda_manufacture.solinda_manufacture'].search([]),
#         })

#     @http.route('/solinda_manufacture/solinda_manufacture/objects/<model("solinda_manufacture.solinda_manufacture"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('solinda_manufacture.object', {
#             'object': obj
#         })
