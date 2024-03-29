# -*- coding: utf-8 -*-

from odoo import models, fields, api

# Clase generada por la relación N:M entre order y product
class order_product(models.Model):
    _name = 'gestionar_recogida_cliente.order_product'
    _description = 'Tabla relación order y product'

    product_id = fields.Many2one('gestionar_recogida_cliente.product', string="Producto")
    order_id = fields.Many2one('gestionar_recogida_cliente.order', string="Pedido", readonly=True)
    quantity = fields.Integer(string="Cantidad")
    product_name = fields.Char(related='product_id.name')