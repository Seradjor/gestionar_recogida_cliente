# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class gestionar_recogida_cliente(models.Model):
#     _name = 'gestionar_recogida_cliente.gestionar_recogida_cliente'
#     _description = 'gestionar_recogida_cliente.gestionar_recogida_cliente'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
