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
    ) 

    @api.onchange("discount")
    def _onchange_discount_percent(self):
        if self.discount:
            total = self.product_uom_qty * self.price_unit
            t_discount_fixed = (self.discount * total) / 100

            if self.discount_fixed != t_discount_fixed:
                self.discount_fixed = t_discount_fixed

    @api.onchange("discount_fixed")
    def _onchange_discount_fixed(self):
        if self.discount_fixed:
            total = self.product_uom_qty * self.price_unit
            t_discount = (self.discount_fixed / total) * 100
            if self.discount != t_discount:
                self.discount = t_discount

  #todo 

    @api.depends(
        "product_uom_qty", "discount", "price_unit", "tax_id", "discount_fixed"
    )
    
    def _prepare_invoice_line(self):
        res = super(SaleOrderLine, self)._prepare_invoice_line()
        res.update({"discount_fixed": self.discount_fixed})
        return res
