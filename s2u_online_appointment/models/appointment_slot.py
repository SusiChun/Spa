# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date as py_date            # untuk .weekday()
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
import pytz
COMPANY_TZ = pytz.timezone('Asia/Jakarta')
class AppointmentSlot(models.Model):
    _name = 's2u.appointment.slot'
    _order = 'date desc'
    _description = "Appointment Slot"
    
    @api.model
    def _get_week_days(self):
        return [
            ('0', _('Senin ')),
            ('1', _('Selasa')),
            ('2', _('Rabu')),
            ('3', _('Kamis')),
            ('4', _('Jumat')),
            ('5', _('Sabtu')),
            ('6', _('Minggu'))
        ]

    employee_id = fields.Many2one('hr.employee', string='Therapist', required=True)
    user_id = fields.Many2one('res.users', string='User',related='employee_id.user_id', store=True)
    date =fields.Date(string='Tanggal')
    day = fields.Selection(
        selection=_get_week_days,
        string="Hari",
        compute='_compute_day',
        store=True,
        readonly=True,  # hapus readonly jika Anda ingin editable
    )
    slot = fields.Float('Jam')
    start_hour = fields.Float(string='Jam Mulai' ,default=10.0,          # ← default pukul 10 : 00
    digits=(16, 2), )  # 13.0
    end_hour = fields.Float(string='Jam Selesai' ,default=22.0,          # ← default pukul 10 : 00
    digits=(16, 2), )
    sale_order_ids = fields.One2many(
        comodel_name='sale.order',
        inverse_name='therapist_id',  # ← relasi via therapist saja
        compute='_compute_orders',
        store=False)
    sale_order_count = fields.Integer(
        compute='_compute_orders')

    is_available = fields.Boolean(
        string='Available',
        compute='_compute_orders')
    time_range = fields.Char(
        compute='_compute_time_range', store=False)

    def _compute_time_range(self):
        for rec in self:
            sh = rec.start_hour or 0.0
            eh = rec.end_hour or 0.0
            rec.time_range = '%02d:%02d – %02d:%02d' % (
                int(sh), int(round((sh % 1) * 60)),
                int(eh), int(round((eh % 1) * 60)),
            )
    @api.depends('date')
    def _compute_day(self):
        for rec in self:
            if rec.date:
                # rec.date sudah bertipe datetime.date di Odoo 14+
                # Untuk versi lama, gunakan: dt = fields.Date.from_string(rec.date)
                dt = rec.date if isinstance(rec.date, py_date) \
                    else fields.Date.from_string(rec.date)

                rec.day = str(dt.weekday())  # Senin = 0 … Minggu = 6
            else:
                rec.day = False

    # ------------------------------------------------------------------
    @api.depends('date', 'start_hour', 'end_hour', 'employee_id')
    def _compute_orders(self):
        SaleOrder = self.env['sale.order'].sudo()
        today=fields.Date.today()
        for slot in self:
            slot.sale_order_ids = False
            slot.sale_order_count = 0
            slot.is_available = False

            if not (slot.date and slot.employee_id
                    and slot.start_hour is not False
                    and slot.end_hour is not False):
                continue

            # 1️⃣  Slot di zona lokal **aware**
            slot_start_local = COMPANY_TZ.localize(
                datetime.combine(slot.date, time.min) + relativedelta(hours=slot.start_hour)
            )
            slot_end_local = COMPANY_TZ.localize(
                datetime.combine(slot.date, time.min) + relativedelta(hours=slot.end_hour)
            )

            # 2️⃣  Batas tanggal utk query ke DB (UTC naïve)
            day_start_utc = slot_start_local.astimezone(pytz.utc).replace(tzinfo=None,
                                                                          hour=0, minute=0, second=0, microsecond=0)
            day_end_utc = slot_end_local.astimezone(pytz.utc).replace(tzinfo=None,
                                                                      hour=23, minute=59, second=59, microsecond=999999)

            raw_orders = SaleOrder.search([
                ('therapist_id', '=', slot.employee_id.id),
                ('date_order', '>=', day_start_utc),
                ('date_order', '<=', day_end_utc),
                ('state', 'in', ('draft', 'sale', 'done')),
            ])

            # 3️⃣  Filter overlap sepenuhnya di LOCAL tz (semua **aware**)
            def _overlap_local(order):
                o_start = fields.Datetime.context_timestamp(order, order.date_order)
                o_end = fields.Datetime.context_timestamp(order, order.end_datetime)
                return (o_start < slot_end_local) and (o_end > slot_start_local)

            orders = raw_orders.filtered(_overlap_local)

            slot.sale_order_ids = orders
            slot.sale_order_count = len(orders)
            if slot.date == today:
                slot.is_available = slot.employee_id.available_now
            else:
                slot.is_available = True