# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from email.utils import formataddr

from datetime import datetime, timedelta


class order(models.Model):
    _name = 'gestionar_recogida_cliente.order'
    _description = 'Pedido de cliente'
    _rec_name = 'code'

    code = fields.Char(size = 7, string="Número", readonly=True, default=lambda self: self._generate_order_number())
    state_order = fields.Selection([('0','Iniciado'),('1','Realizado'),('2','Preparado'),('3','Confirmada recogida'),('4','Recogido')],default = '0', required=True, string="Estado")
    order_date = fields.Date(string="Fecha pedido", required=True, default=lambda self:datetime.today())
    pick_up_date = fields.Datetime(string="Fecha recogida")

    # Enlace con client
    client_id = fields.Many2one('res.partner', required=True, string="Cliente") # Me sale el siguiente error con required= -> odoo.schema: Table 'gestionar_recogida_cliente_order': unable to set NOT NULL on column 'client_id' 

    # Enlace con product a través de order_product
    products_ids = fields.One2many('gestionar_recogida_cliente.order_product', 'order_id', string="Productos")


    # Generamos número de pedido automáticamente
    @api.model
    def _generate_order_number(self):
        today = datetime.today()
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
        tabla_productos = "<table style='border-collapse:collapse'><tr><th style='border:1px solid black; padding:3px; text-align:left'>Producto</th><th style='border:1px solid black; padding:3px; text-align:center'>Cantidad</th><th style='border:1px solid black; padding:3px; text-align:center'>Pallets</th></tr>"

        # Rellenamos los datos con los productos del pedido.
        for producto in self.products_ids:
            tabla_productos += f"<tr><td style='border:1px solid black; padding:3px; text-align:left'>{producto.product_id.name}</td><td style='border:1px solid black; padding:3px; text-align:center'>{producto.quantity:,}</td><td style='border:1px solid black; padding:3px; text-align:center'>{(producto.quantity/1000):.0f}</td></tr>"

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
        body_html = f"<h1>Bodega DAM, S.L.</h1><p>Estimado {self.client_id.name},<br><br>Le informamos que su pedido con el número {self.code} ya está listo para ser recogido. <br><br>Detalle pedido:  <br><br>{tabla_productos.replace(',', '.')} <br><br>Enlace de recogida: <a href='http://localhost:8069/confirmpickup/{self.id}'>gestionar recogida</a></p>"
        
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
 

    # Cálculo de horas disponibles de recogida
    
    def options_date_pick_up(self):
        # Guardamos recogidas 
        days_pick_up = []
        orders = self.env['gestionar_recogida_cliente.order'].search([])
        for order in orders:
            if order.pick_up_date: # Si tiene ya fecha de recogida
                day_pick_up = order.pick_up_date + timedelta(hours=2) # Para corregir cálculo erróneo de hora !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                print(day_pick_up)
                days_pick_up.append(day_pick_up)
                
        
        print(days_pick_up)
        
        # Creamos variable donde guardar las fechas de recogida
        options = []

        # Obtenemos la fecha de hoy
        today = datetime.now()

        # Calculamos la fecha de inicio y fin de las próximas dos semanas
        start_day = today + timedelta(days=1)  # Excluimos el día de hoy, el mismo día no habrán recogidas para organizar el almacén con tiempo
        print(start_day)
        final_day = start_day + timedelta(weeks=2) # Vamos a obtener fechas para las próximas 2 semanas
        print(final_day)

        # Iteramos sobre cada día en el rango de fechas
        while start_day <= final_day:
            # Excluimos los sábados (weekday() devuelve 5 para sábado) y domingos (6 para domingo)
            if start_day.weekday() < 5:  # Si no es sábado ni domingo
                print(start_day)

                # Establecemos la hora de inicio y fin para cada día
                start_hour = datetime(start_day.year, start_day.month, start_day.day, 8, 0, 0) # La primera recogida será a las 08:00
                final_hour = datetime(start_day.year, start_day.month, start_day.day, 17, 0, 0) # La última recogida será a las 17:00

                # Añadimos todas las horas dentro del rango para ese día
                while start_hour <= final_hour:
                    print(start_hour)
                    if start_hour not in days_pick_up:
                        options.append(start_hour)
                    start_hour += timedelta(hours=1)


            # Pasamos al siguiente día
            start_day += timedelta(days=1)

        # Devolvemos la lista de opciones de datetime
        for i in options:
            print(i)
        return options
