# -*- coding: utf-8 -*-
# from odoo import http


# class ScExpense(http.Controller):
#     @http.route('/sc_expense/sc_expense', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sc_expense/sc_expense/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sc_expense.listing', {
#             'root': '/sc_expense/sc_expense',
#             'objects': http.request.env['sc_expense.sc_expense'].search([]),
#         })

#     @http.route('/sc_expense/sc_expense/objects/<model("sc_expense.sc_expense"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sc_expense.object', {
#             'object': obj
#         })
