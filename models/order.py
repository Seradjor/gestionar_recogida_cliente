# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

import datetime


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, string="Número", readonly=True, default=lambda self: self._generate_order_number())
    state_order = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Confirmada recogida'),('4','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido", required=True, default=lambda self:datetime.date.today())
    pick_up_date = fields.Datetime(string="Fecha recogida")

    # Enlace con client
    client_id = fields.Many2one('res.partner', required=True, string="Cliente") # Me sale el siguiente error con required= -> odoo.schema: Table 'gestionar_recogida_cliente_order': unable to set NOT NULL on column 'client_id' 

    # Enlace con product a través de order_product
    products_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'order_id', string="Productos")


    # Generamos número de pedido automáticamente
    @api.model
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
            
    # Comprobamos que la fecha de recogida es posterior a la fecha de pedido y establecemos el valor 00 tanto a los minutos como los segundos para cada nuevo registro
    @api.onchange('pick_up_date')
    def _onchange_pick_up_date(self):
        if self.pick_up_date:
            self.pick_up_date = self.pick_up_date.replace(minute=0, second=0)
        if self.pick_up_date.date() < self.order_date:
            raise ValidationError('La fecha de recogida no puede ser anterior a la fecha de pedido.')

    # El valor en el campo pick_up_date no se puede repetir, solo puede haber una carga por hora.
    _sql_constraints = [
        ('pick_up_uniq', 'unique(pick_up_date)', 'Ya existe una recogida en dicha franja horaria, elija otra opción.'),
    ]

    # Cambio stocks (de disponible a reservado)
    @api.model
    def _stock_change_disponible_reserved(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.write({'reserved_stock': product.reserved_stock + quantity})

            # Actualiza el stock disponible del producto
            product.write({'disponible_stock': product.disponible_stock - quantity})

    # Cambio stocks (de reservado a disponible)
    @api.model
    def _stock_change_reserved_disponible(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.write({'reserved_stock': product.reserved_stock - quantity})

            # Actualiza el stock disponible del producto
            product.write({'disponible_stock': product.disponible_stock + quantity})            

    # Cambio stocks (pedido entregado)
    @api.model
    def _stock_change_reserved(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.write({'reserved_stock': product.reserved_stock - quantity})


    """ FUNCIONES BOTONERAS """

    # Función retroceder estado
    @api.model
    def state_order_back(self):
        self.ensure_one()
        self.state_order = str(int(self.state_order) - 1)
        if self.state_order == '1':  # Si pasa al estado "Realizado"
            self._stock_change_reserved_disponible()

    # Función avanzar estado
    @api.model
    def state_order_forward(self):
        self.ensure_one()
        self.state_order = str(int(self.state_order) + 1)
        if self.state_order == '2':  # Si pasa al estado "Preparado"
            self._stock_change_disponible_reserved()
        if self.state_order == '4':  # Si pasa al estado "Recogido"
            self._stock_change_reserved()
