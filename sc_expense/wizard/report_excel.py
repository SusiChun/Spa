from odoo import models

class PengeluaranXlsx(models.AbstractModel):
    _name = 'report.sc_expense.report_pengeluaran_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, obj):
        wizard_data = data['form']
        date_from = wizard_data['date_from']
        date_to = wizard_data['date_to']

        pengeluaran_ids = self.env['pengeluaran.pengeluaran'].search([
            ('tanggal', '>=', date_from),
            ('tanggal', '<=', date_to)
        ])

        sheet = workbook.add_worksheet('Pengeluaran')
        bold = workbook.add_format({'bold': True})

        row = 0
        sheet.write(row, 0, 'Tanggal', bold)
        sheet.write(row, 1, 'Keterangan', bold)
        sheet.write(row, 2, 'Subtotal', bold)
        row = 1
        grand_total = 0.0

        for rec in pengeluaran_ids:
            for line in rec.line_ids:
                sheet.write(row, 0, str(rec.tanggal))
                sheet.write(row, 1, line.keterangan)
                sheet.write(row, 2, line.subtotal)
                row += 1
            grand_total += rec.total

            # grand total row
            sheet.write(row, 1, 'Grand Total', bold)
            sheet.write(row, 2, grand_total, bold)