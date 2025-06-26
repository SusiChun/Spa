from odoo import models, fields

class PengeluaranWizard(models.TransientModel):
    _name = 'pengeluaran.wizard'
    _description = 'Export Pengeluaran ke Excel'

    date_from = fields.Date(string="Dari Tanggal", default=fields.Date.context_today)
    date_to = fields.Date(string="Sampai Tanggal", default=fields.Date.context_today)

    def export_excel(self):
        data = {
            'form': self.read()[0]
        }
        return self.env.ref('sc_expense.report_pengeluaran_xlsx').report_action(self, data=data)