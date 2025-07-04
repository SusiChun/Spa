# -*- coding: utf-8 -*-
# from odoo import http


# class ScCashSummary(http.Controller):
#     @http.route('/sc_cash_summary/sc_cash_summary', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sc_cash_summary/sc_cash_summary/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sc_cash_summary.listing', {
#             'root': '/sc_cash_summary/sc_cash_summary',
#             'objects': http.request.env['sc_cash_summary.sc_cash_summary'].search([]),
#         })

#     @http.route('/sc_cash_summary/sc_cash_summary/objects/<model("sc_cash_summary.sc_cash_summary"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sc_cash_summary.object', {
#             'object': obj
#         })
