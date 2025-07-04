from odoo import api, fields, models
import pytz
COMPANY_TZ = pytz.timezone('Asia/Jakarta')
from datetime import datetime
class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    available_now = fields.Boolean(
        string='Available Now',
        compute='_compute_available_now',
        store=False)

    def _compute_available_now(self):
        SaleOrder = self.env['sale.order'].sudo()
        now_local = datetime.now(COMPANY_TZ)
        today = now_local.date()
        now_hour = now_local.hour + now_local.minute / 60.0

        for emp in self:
            # Ambil semua order hari ini milik therapist
            orders = SaleOrder.search([
                ('therapist_id', '=', emp.id),
                ('date_order', '>=',
                 COMPANY_TZ.localize(datetime.combine(today, datetime.min.time()))
                 .astimezone(pytz.utc)),  # awal hari UTC
                ('date_order', '<',
                 COMPANY_TZ.localize(datetime.combine(today, datetime.max.time()))
                 .astimezone(pytz.utc)),  # akhir hari UTC
                ('state', 'in', ('draft', 'sale', 'done')),
            ])

            busy = False
            for o in orders:
                # jam mulai & selesai menurut lokal
                o_start_local = fields.Datetime.context_timestamp(o, o.date_order)
                o_hour = o_start_local.hour + o_start_local.minute / 60.0
                if o_hour >= (o.start_hour or 0) and o_hour < (o.end_hour or 0):
                    busy = True
                    break
            emp.available_now = not busy