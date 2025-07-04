from odoo import api, fields, models,_
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
class SO(models.Model):
    _inherit = 'sale.order'

    therapist_id    = fields.Many2one('hr.employee',required=True,string='Therapist',        domain="[('id', 'in', available_therapist_ids)]",)
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

    ], string='Tipe Pembayaran', copy=False)
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

    # Kolom helper untuk domain
    available_therapist_ids = fields.Many2many(
        'hr.employee',
        compute='_compute_available_therapist_ids',
        string='Therapists Tersedia',
        compute_sudo=True,  # hindari masalah hak akses
        store=False,
    )
    end_datetime = fields.Datetime(
        string='Selesai',
        compute='_compute_end_datetime',
        store=True)

    # ------------------------------------------------
    @api.depends('date_order', 'start_hour', 'end_hour')
    def _compute_end_datetime(self):
        for so in self:
            if so.date_order:
                duration = (so.end_hour or 0.0) - (so.start_hour or 0.0)
                so.end_datetime = so.date_order + relativedelta(hours=duration)
            else:
                so.end_datetime = False
    @api.depends('date_order')
    def _compute_available_therapist_ids(self):
        Slot = self.env['s2u.appointment.slot']
        for order in self:
            if not order.date_order:
                order.available_therapist_ids = False
                continue

            # 1) Konversi date_order (UTC) → tanggal lokal user
            #    Agar “05‑Jul‑2025 02:00 UTC” tetap dianggap 04‑Jul bila user di GMT‑7
            dt_local = fields.Datetime.context_timestamp(order, order.date_order)
            order_date_only = dt_local.date()  # tipe datetime.date

            # 2) Ambil therapist yang punya slot di tanggal tersebut
            therapist_set = Slot.search([
                ('date', '=', order_date_only)
            ]).mapped('employee_id')

            order.available_therapist_ids = therapist_set


    # ----------  logika perhitungan  ----------
    @api.depends('start_hour', 'end_hour')
    def _compute_total_jam(self):
        for rec in self:
            # kalau salah satu kosong, jadikan 0.0
            rec.total_jam = (rec.end_hour or 0.0) - (rec.start_hour or 0.0)

class SO_Line(models.Model):
    _inherit = 'sale.order.line'

    therapist_id    = fields.Many2one('hr.employee',related='order_id.therapist_id',string='Therapist')
