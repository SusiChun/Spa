# Copyright 2017-20 kbizsoft
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount_fixed = fields.Float(
        string="Tips",
        digits="Product Price",
        help="Fixed amount discount.",
        related="product_id.standard_price"
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_untaxed_after_discount = fields.Monetary(
        string="Total After Tips",
        compute="_compute_amount_untaxed_after_discount",
        store=True,
        currency_field="currency_id",
    )

    @api.depends('order_line.price_subtotal','order_line.discount_fixed')
    def _compute_amount_untaxed_after_discount(self):
        """
        Ambil subtotal dari semua order_line (sudah termasuk diskon).
        """
        for order in self:
            order.amount_untaxed_after_discount = sum(order.order_line.mapped('price_subtotal')) - sum(order.order_line.mapped('discount_fixed'))




