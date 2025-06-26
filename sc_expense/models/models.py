# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Pengeluaran(models.Model):
    _name = "pengeluaran.pengeluaran"
    _description = "Pengeluaran"

    name = fields.Char(string="No. Dokumen", required=True, default="New", copy=False)
    tanggal = fields.Date(string="Tanggal", required=True,default=fields.Date.context_today)
    line_ids = fields.One2many("pengeluaran.line", "pengeluaran_id", string="Detail")
    total = fields.Float(string="Total", compute="_compute_total", store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed')
    ], string="Status", default='draft', tracking=True)
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pengeluaran.seq') or 'New'
        return super().create(vals)

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for rec in self:
            rec.total = sum(line.subtotal for line in rec.line_ids)

    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_set_draft(self):
        self.write({'state': 'draft'})


class PengeluaranLine(models.Model):
    _name = "pengeluaran.line"
    _description = "Detail Pengeluaran"

    pengeluaran_id = fields.Many2one("pengeluaran.pengeluaran", string="Pengeluaran", required=True, ondelete="cascade")
    keterangan = fields.Text(string="Keterangan")
    subtotal = fields.Float(string="subtotal")
