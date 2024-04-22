# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from email.utils import formataddr

import datetime


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, string="Número", readonly=True, default=lambda self: self._generate_order_number())
    state_order = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Confirmada recogida'),('4','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido", required=True, default=lambda self:datetime.date.today())
    pick_up_date = fields.Datetime(string="Fecha recogida")
    ready = fields.Boolean(string="Listo para recoger")

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
    def _stock_change_disponible_reserved(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.reserved_stock += quantity
            """ product.write({'reserved_stock': product.reserved_stock + quantity}) """

            # Actualiza el stock disponible del producto
            product.disponible_stock -= quantity
            """ product.write({'disponible_stock': product.disponible_stock - quantity}) """

    # Cambio stocks (de reservado a disponible)
    def _stock_change_reserved_disponible(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.write({'reserved_stock': product.reserved_stock - quantity})

            # Actualiza el stock disponible del producto
            product.write({'disponible_stock': product.disponible_stock + quantity})            

    # Cambio stocks (pedido entregado)
    def _stock_change_reserved(self):
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Actualiza el stock reservado del producto
            product.write({'reserved_stock': product.reserved_stock - quantity})

    # Comprobar stocks disponibles para validar preparación de pedidos.
    def _check_disponible_stocks(self):
        enough_stock = True
        error_message = f"Faltan los siguientes productos: "
        for line in self.products_ids:
            product = line.product_id
            quantity = line.quantity

            # Comprobamos si hay suficiente stock
            if product.disponible_stock < quantity:
                enough_stock = False
                error_message += f"\n- {product.name} ({-(product.disponible_stock - quantity):,})".replace(',', '.') # :,})".replace(',', '.') -> pongo separador de miles a la cantidad obtenida con ',', reemplazándolo por '.' después.

        print(error_message)
        return [enough_stock,error_message]

    # Envío del correo de confirmación de pedido preparado para su recogida al cliente.
    def email_confirm_pickup(self):
    
        # Creamos la tabla con <html> que mostraremos luego en el correo
        # Creamos inicio de la tabla
        tabla_productos = "<table style='border-collapse:collapse'><tr><th style='border:1px solid black; padding:3px; text-align:left'>Producto</th><th style='border:1px solid black; padding:3px; text-align:center'>Cantidad</th></tr>"

        # Rellenamos los datos con los productos del pedido.
        for producto in self.products_ids:
            tabla_productos += f"<tr><td style='border:1px solid black; padding:3px; text-align:left'>{producto.product_id.name}</td><td style='border:1px solid black; padding:3px; text-align:center'>{producto.quantity:,}</td></tr>"

        # Cerramos tabla
        tabla_productos += "</table>"

        # Declaramos parámetros
        Mail = self.env['mail.mail']
        email_to = f"{self.client_id.email}"
        email_from = "seradjor@gmail.com"
        nombre_empresa = 'Bodega DAM, S.L.'
        email_from_formatted = formataddr((nombre_empresa, email_from))
        subject = f"Bodega DAM, S.L., Pedido {self.code}"
        print(subject)
        body_html = f"<h1>Bodega DAM, S.L.</h1><p>Estimado {self.client_id.name},<br><br>Le informamos que su pedido con el número {self.code} ya está listo para ser recogido. <br><br>Detalle pedido:  <br><br>{tabla_productos.replace(',', '.')} <br><br>Enlace de recogida: XXXX</p>"
        
        mail_values = {
            'email_to': email_to,
            'email_from': email_from_formatted,
            'subject': subject,
            'body_html': body_html,
        }
        
        # Enviamos el correo
        mail = Mail.create(mail_values)
        mail.send()


    """ FUNCIONES BOTONERAS """

    # Función retroceder estado
    def state_order_back(self):
        self.ensure_one()
        if self.state_order == '2':  # Si está en el estado "Preparado"
            self._stock_change_reserved_disponible()
        self.state_order = str(int(self.state_order) - 1)

    # Función avanzar estado
    def state_order_forward(self):
        self.ensure_one()
        if self.state_order == '1':  # Si está en el estado "Realizado"
            validation_stock = self._check_disponible_stocks()
            if validation_stock[0] == False:
                raise ValidationError(validation_stock[1])
            self._stock_change_disponible_reserved()
            self.email_confirm_pickup()
        elif self.state_order == '2' and self.pick_up_date == False:  # Si está en el estado "Preparado"
            raise ValidationError('Falta introducir fecha recogida.')
        elif self.state_order == '3':  # Si está en el estado "Confirmada recogida"
            self._stock_change_reserved()
        self.state_order = str(int(self.state_order) + 1)
 