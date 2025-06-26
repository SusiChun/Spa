from odoo import api, fields, models,_
from odoo.exceptions import UserError

class SO(models.Model):
    _inherit = 'sale.order'

    therapist_id    = fields.Many2one('hr.employee',required=True,string='Therapist')
    start_hour      = fields.Float(string='Jam Masuk',required=True, )
    end_hour        = fields.Float(string='Jam Keluar',required=True)
    room            = fields.Selection([
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('05', '04'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
    ], required=True, string='Room', copy=False)
    komisi          = fields.Float(string='Komisi')
    tipe_pembayaran =    fields.Selection([
        ('Cash', 'Cash'),
        ('Debit Mandiri', 'Debit Mandiri'),
        ('Debit BCA', 'Debit BCA'),
        ('Transfer', 'Transfer'),
        ('QRIS', 'QRIS'),

    ], required=True, string='Tipe Pembayaran', copy=False)