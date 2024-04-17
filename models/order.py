# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import datetime


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, string="Número", readonly=True, default=lambda self: self._generate_order_number())
    state = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Confirmada recogida'),('4','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido", default=lambda self:datetime.date.today())
    pick_up_date = fields.Date(string="Fecha recogida")

    # Enlace con client
    client_id = fields.Many2one('res.partner')
    client_name = fields.Char(related='client_id.name', string="Cliente")
    """ HABRÁ QUE RELACIONAR CLIENTE CON PEDIDO DESDE LA BBDD MANUALMENTE """

    # Enlace con product a través de order_product
    products_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'order_id', string="Productos")


    # Generamos número de pedido automáticamente
    def _generate_order_number(self):
        today = datetime.date.today()
        year = str(today.year)
        last_order = self.search([], order='id desc', limit=1)
        if last_order:
            last_code = last_order.code
            last_number = int(last_code[4:])  # Excluyendo la longitud del año, obtenemos los últimos 3 dígitos del código.
            new_number = last_number + 1
            new_code = year + str(new_number).zfill(3)  # Rellenar con ceros a la izquierda
        else:
            new_code = year + '001'
        return new_code
    
    # Comprobación fecha recogiga es posterior a fecha pedido
    @api.constrains('pick_up_date')
    def _check_pick_up_date(self):
        for record in self:
            if record.pick_up_date < record.order_date:
                raise ValidationError('La fecha de recogida no puede ser anterior a la fecha de pedido.')


    """ FUNCIONES BOTONERAS """

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
    

