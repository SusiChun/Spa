from odoo import api, fields, models,_
from odoo.exceptions import UserError

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    sale_order_id = fields.Many2one(
            'sale.order',
            string='Sales Order',
            readonly=True,
            copy=False,
        )

    def action_confirm_to_sale_order(self):
        """Button: buat SO lalu buka form-nya."""
        self.ensure_one()

        # SO sudah ada? buka saja
        # if self.sale_order_id:
        #     return self._action_open_so()
        # else:
        # Pastikan ada partner
        internal_partner_ids = self.partner_ids.filtered(lambda p: p.user_ids)

        # customer candidates = attendee yg bukan internal
        partner_customer = (self.partner_ids - internal_partner_ids)[:1]
        if not partner_customer:
            raise UserError(
                _("Setidaknya satu attendee/customer wajib diisi sebelum membuat Sales Order.")
            )
        internal_user = (internal_partner_ids.mapped('user_ids'))[:1] or self.user_id
        # Siapkan baris produk (ganti ID produk sesuai modul Anda)
        #product_meeting = self.env.ref('product.product_product_4')   # “Consulting Service” contoh
        so_vals = {
            'partner_id': partner_customer.id,      # customer
            'therapist_id': internal_user.id,
            'origin': f"Event: {self.name}",
            'note': f"{self.name}-{self.description}",
            'date_order': self.start or fields.Datetime.now(),
            'order_line': [(0, 0, {
                'name': f"{self.name}",
                'display_type':'line_section'
            })],
        }
        print (so_vals)
        # Buat SO (sudo agar siapa pun user kalender bisa)
        sale_order = (
            self.env['sale.order']
            .sudo()
            .with_context(skip_calendar_event=True)  # hindari loop jika Anda punya logic sebaliknya
            .create(so_vals)
        )
        self.sale_order_id = sale_order.id

        return self._action_open_so()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _action_open_so(self):
        """Return action window ke Sales Order terkait."""
        self.ensure_one()

        if not self.sale_order_id:
            raise UserError("Sales Order belum tersedia.")
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sales Order'),
            'res_model': 'sale.order',
            'res_id': self.sale_order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }