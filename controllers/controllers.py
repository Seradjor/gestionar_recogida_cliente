# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class GestionarRecogidaCliente(http.Controller):
    @http.route('/confirmpickup/<model("gestionar_recogida_cliente.order"):confirm_pick_up>', auth='public', website=True)
    def confirm_pick_up(self, confirm_pick_up, **post):
        pick_up_date = post.get('pick_up_date')  # Obtener la fecha seleccionada en el formulario

        # Si se lanza el formulario, mostraremos guardamos la fecha en el registro y mostramos una pantalla de agradecimiento.
        if pick_up_date:
            confirm_pick_up.write({'pick_up_date': pick_up_date})  # Guardar la fecha en el campo pick_up_date
            confirm_pick_up.state_order_forward() # Avanzamos al siguiente estado del pedido, con lo que ello conlleva según función state_order_forward()
            return http.request.render('gestionar_recogida_cliente.confirmed_pick_up',{
                "confirm_pick_up": confirm_pick_up
            })
        
        # Hasta que no se lance el formulario, mostraremos la página normal con el template "confirm_pick_up"
        else:
            return http.request.render('gestionar_recogida_cliente.confirm_pick_up',{
                "confirm_pick_up": confirm_pick_up
            })
  
        
        """ if http.request.httprequest.method == 'POST':
            pick_up_date = http.request.params.get('pick_up_date')
            # Guardar la fecha de recogida en el objeto confirm_pick_up
            confirm_pick_up.write({'pick_up_date': pick_up_date})
            # Guardar los cambios en la base de datos
            confirm_pick_up.flush()
            # Devolver la vista con un indicador de éxito
            return http.request.render('gestionar_recogida_cliente.confirm_pick_up',{
                "confirm_pick_up": confirm_pick_up,
                "success": True  # Puedes enviar un indicador de éxito para mostrar un mensaje si es necesario
            })
        else:
            # Si es una solicitud GET, simplemente renderiza la página
            return http.request.render('gestionar_recogida_cliente.confirm_pick_up',{
                "confirm_pick_up": confirm_pick_up,
                "success": False  # Indicador de que no se ha procesado ningún formulario todavía
            }) """
        