# -*- coding: utf-8 -*-
{
    'name': "gestionar_recogida_cliente",

    'summary': """
        Planificar recogidas de pedidos de clientes. """,

    'description': """
        El objetivo de este módulo es la planificación de la entrega de pedidos de cliente, en contacto directo con este.

        Cada 12 horas se comprobará, por orden de entrada en el sistema, si los pedidos de cliente registrados están listos para su entrega (al tener suficiente stock de los productos solicitados).

        En el momento que un pedido esté listo, el producto se bloqueará para dicho pedido y se le hará llegar al cliente un correo electrónico con el detalle de dicho pedido y un enlace para gestionar su recogida.

        Dicho enlace le llevará a una página web con información de días y horas disponibles (en el momento que accede al enlace) por parte del almacén para realizar la entrega del pedido. El cliente seleccionará las opciones que más le interesen.

        Dicha selección la registararemos en el sistema y se bloqueará ese día y hora en la planificación del almacén para no solapar entregas o recogidas de otros pedidos.
    """,

    'author': "Sergio Adell",
    'website': "https://seradjor.github.io/gestionar_recogida_cliente/",

    # Indicamos que es una aplicación
    'application': True,

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productivity',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
