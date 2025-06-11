# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd.
# - © Technaureus Info Solutions Pvt. Ltd 2023. All rights reserved.

{
    'name': 'Thermal Sale',
    'version': '16.0.0.0',
    'category': 'Accounting',
    'summary': 'Print Thermal Sale',
    'sequence': 1,
    'author': 'Technaureus Info Solutions Pvt. Ltd.',
    'website': "http://www.technaureus.com/",
    'price': 9,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'depends': ['sale', 'sale_management'],
    'data': [
        'data/paper_format.xml',
        'report/sale_report.xml',
        'report/report_sale.xml',
        'report/sale_external_layout.xml'
    ],
    'qweb': [],
    'demo': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
