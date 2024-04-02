# -*- coding: utf-8 -*-

from odoo import models, fields, api


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, required=True, string="Número")
    state = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido")
    pick_up_date = fields.Date(string="Fecha recogida")

    # Enlace con client
    """ client_id = fields.Many2one('res_partner')
    client_name = fields.Char(related='client_id.name')
    HABRÁ QUE RELACIONAR CLIENTE CON PEDIDO DESDE LA BBDD MANUALMENTE """

    # Enlace con product a través de order_product
    products_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'order_id', string="Productos")


    # Función cambio de estado pedido
    def order_ready(self):
        print()
    

