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
        now_local = datetime.now(COMPANY_TZ)
        today = now_local.date()

        now_hour = now_local.hour + now_local.minute / 60.0
        now_utc = datetime.now(tz=COMPANY_TZ).astimezone(pytz.utc)
        SaleOrder = self.env['sale.order'].sudo()

        # ‑‑‑ Waktu “sekarang” dalam UTC (karena database Odoo disimpan UTC)
        now_utc = datetime.now(tz=COMPANY_TZ).astimezone(pytz.utc)

        for emp in self:
            # Order yang *overlap* dgn now:
            #   start ≤ now < end
            overlap_domain = [
                ('therapist_id', '=', emp.id),
                ('state', 'in', ('draft', 'sale', 'done')),  # sesuaikan status aktif
                ('date_order', '<=', now_utc),
                ('end_datetime', '>', now_utc),
            ]
            # search_count ⇒ lebih hemat daripada search lalu len()
            busy = bool(SaleOrder.search_count(overlap_domain))
            emp.available_now = not busy