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
    total_jam = fields.Float(
        string='Ttl Jam',
        compute='_compute_total_jam',  # nama fungsi compute
        readonly=True  # opsional: supaya user tidak bisa mengubah manual
    )
    state = fields.Selection(
        selection=[
            ('draft', "Mulai"),
            ('sent', " "),
            ('sale', "Selesai"),
            ('done', "Locked"),
            ('cancel', "Cancelled"),
        ],
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')
    # ----------  logika perhitungan  ----------
    @api.depends('start_hour', 'end_hour')
    def _compute_total_jam(self):
        for rec in self:
            # kalau salah satu kosong, jadikan 0.0
            rec.total_jam = (rec.end_hour or 0.0) - (rec.start_hour or 0.0)