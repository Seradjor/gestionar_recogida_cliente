# -*- coding: utf-8 -*-

from odoo import models, fields, api


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, required=True, string="Número")
    state = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Confirmada recogida'),('4','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido")
    pick_up_date = fields.Date(string="Fecha recogida")

    # Enlace con client
    client_id = fields.Many2one('res.partner')
    client_name = fields.Char(related='client_id.name', string="Cliente")
    """ HABRÁ QUE RELACIONAR CLIENTE CON PEDIDO DESDE LA BBDD MANUALMENTE """

    # Enlace con product a través de order_product
    products_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'order_id', string="Productos")


    # Función confirmar pedido
    def state_1(self):
        self.write({'state' : '1'})

    # Función retroceder estado
    def state_back(self):
        if self.state == '2':
            self.write({'state' : '1'}) 
        elif self.state == '3':
            self.write({'state' : '2'})
        elif self.state == '4':
            self.write({'state' : '3'}) 
        else: 
            pass

    # Función avanzar estado
    def state_forward(self):
        if self.state == '1':
            self.write({'state' : '2'})
        elif self.state == '2':
            self.write({'state' : '3'}) 
        elif self.state == '3':
            self.write({'state' : '4'}) 
        else: 
            pass
    

