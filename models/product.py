# -*- coding: utf-8 -*-

from odoo import models, fields, api


class product(models.Model):
    _name = 'gestionar_recogida_cliente.product'
    _description = 'Producto solicitado en un pedido'
    _rec_name = 'code'

    code = fields.Char(size = 6, required=True, string="Código")
    name = fields.Char(required=True, string="Nombre")
    unit = fields.Char(string="Unidad de medida")
    disponible_stock = fields.Integer(string="Stock disponible")
    reserved_stock = fields.Integer(string="Stock reservado")

    # Enlace con order a través de order_product
    orders_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'product_id', string="Pedidos")


    


    