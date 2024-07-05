# -*- coding: utf-8 -*-
# from odoo import http


# class FreightManagement(http.Controller):
#     @http.route('/freight_management/freight_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/freight_management/freight_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('freight_management.listing', {
#             'root': '/freight_management/freight_management',
#             'objects': http.request.env['freight_management.freight_management'].search([]),
#         })

#     @http.route('/freight_management/freight_management/objects/<model("freight_management.freight_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('freight_management.object', {
#             'object': obj
#         })

