# -*- coding: utf-8 -*-
# from odoo import http


# class GestionarRecogidaCliente(http.Controller):
#     @http.route('/gestionar_recogida_cliente/gestionar_recogida_cliente/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestionar_recogida_cliente/gestionar_recogida_cliente/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestionar_recogida_cliente.listing', {
#             'root': '/gestionar_recogida_cliente/gestionar_recogida_cliente',
#             'objects': http.request.env['gestionar_recogida_cliente.gestionar_recogida_cliente'].search([]),
#         })

#     @http.route('/gestionar_recogida_cliente/gestionar_recogida_cliente/objects/<model("gestionar_recogida_cliente.gestionar_recogida_cliente"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestionar_recogida_cliente.object', {
#             'object': obj
#         })
