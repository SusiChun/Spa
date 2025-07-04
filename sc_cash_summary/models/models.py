
from odoo import models, fields, tools
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta

class sc_cash_summary(models.Model):
    _name = "cash.summary"
    _description = "Cash Summary"
    _auto = False
    _rec_name = "date"

    date = fields.Date(string="Tanggal", readonly=True)
    komisi = fields.Float(string="Komisi", readonly=True)
    amount_paket = fields.Float(string="Paket", readonly=True)
    amount_minuman = fields.Float(string="Minuman", readonly=True)
    revenue = fields.Float(string="Pendapatan", readonly=True)
    expense = fields.Float(string="Pengeluaran", readonly=True)
    amount_cash = fields.Float(string="Tunai", readonly=True)
    amount_debit_mandiri = fields.Float(string="Mandiri", readonly=True)
    amount_debit_bca = fields.Float(string="BCA", readonly=True)
    amount_transfer = fields.Float(string="Transfer", readonly=True)
    amount_qris = fields.Float(string="QRIS", readonly=True)
    net = fields.Float(string="Saldo Akhir", readonly=True)


    sale_line_ids = fields.Many2many(
        'sale.order.line', compute='_compute_related_lines',
        string='Detail Penjualan', store=False)
    expense_line_ids = fields.Many2many(
        'pengeluaran.line', compute='_compute_related_lines',
        string='Detail Pengeluaran', store=False)

    sale_line_count = fields.Integer(
        string='# Penjualan', compute='_compute_related_lines')
    expense_line_count = fields.Integer(
        string='# Pengeluaran', compute='_compute_related_lines')

    # -------------- Core --------------
    def _compute_related_lines(self):
        """Link semua order_line & pengeluaran_line yg jatuh di tanggal ini."""
        SaleLine = self.env['sale.order.line']
        ExpenseLine = self.env['pengeluaran.line']

        for rec in self:
            if not rec.date:
                rec.sale_line_ids = False
                rec.expense_line_ids = False
                rec.sale_line_count = 0
                rec.expense_line_count = 0
                continue

            start_dt = datetime.combine(rec.date, time.min)
            end_dt = start_dt + relativedelta(days=1)

            sale_lines = SaleLine.search([
                ('order_id.date_order', '>=', start_dt),
                ('order_id.date_order', '<', end_dt),
                ('order_id.state', 'in', ('draft', 'sale', 'done')),
                ('display_type','!=','line_section')
            ])
            expense_lines = ExpenseLine.search([
                ('pengeluaran_id.tanggal', '=', rec.date),
            ])

            rec.sale_line_ids = sale_lines
            rec.expense_line_ids = expense_lines
            rec.sale_line_count = len(sale_lines)
            rec.expense_line_count = len(expense_lines)




    def init(self):
        tools.drop_view_if_exists(self._cr, "cash_summary")
        self._cr.execute("""
        CREATE OR REPLACE VIEW cash_summary AS (
            /* ==========================================================
               1. AGREGASI PENJUALAN PER CHANNEL PEMBAYARAN
               ========================================================== */
            WITH so_agg AS (
                SELECT
                    so.date_order::date AS date,
                    SUM(so.komisi)          AS komisi,
                    SUM(CASE WHEN so.tipe_pembayaran = 'Cash'
                             THEN sol.price_subtotal ELSE 0 END)          AS amount_cash,

                    SUM(CASE WHEN so.tipe_pembayaran = 'Debit Mandiri'
                             THEN sol.price_subtotal ELSE 0 END)          AS amount_debit_mandiri,

                    SUM(CASE WHEN so.tipe_pembayaran = 'Debit BCA'
                             THEN sol.price_subtotal ELSE 0 END)          AS amount_debit_bca,

                    SUM(CASE WHEN so.tipe_pembayaran = 'Transfer'
                             THEN sol.price_subtotal ELSE 0 END)          AS amount_transfer,

                    SUM(CASE WHEN so.tipe_pembayaran = 'QRIS'
                             THEN sol.price_subtotal ELSE 0 END)          AS amount_qris,

                    /* ------ Pendapatan per TAG produk ------ */
                    SUM(CASE WHEN tag_paket.id    IS NOT NULL          THEN sol.price_subtotal ELSE 0 END) AS amount_paket,
                    SUM(CASE WHEN tag_minuman.id  IS NOT NULL          THEN sol.price_subtotal ELSE 0 END) AS amount_minuman,

                    /* ------ Total pendapatan hari tsb (semua produk & channel) ------ */
                    SUM(sol.price_subtotal)             AS revenue
                    FROM  sale_order_line                 sol
                    JOIN  sale_order                      so   ON so.id = sol.order_id
                    /* --- ke product & tag --- */
                    JOIN  product_product                 pp   ON pp.id = sol.product_id
                    JOIN  product_template                pt   ON pt.id = pp.product_tmpl_id

                /* Tag “Paket”  */
                LEFT  JOIN product_tag_product_template_rel rel_paket
                       ON rel_paket.product_template_id = pt.id
                LEFT  JOIN product_tag                 tag_paket
                       ON tag_paket.id = rel_paket.product_tag_id
                      AND tag_paket.name->>'en_US' ILIKE '%paket%'

                /* Tag “Minuman” */
                LEFT  JOIN product_tag_product_template_rel rel_min
                       ON rel_min.product_template_id = pt.id
                LEFT  JOIN product_tag                 tag_minuman
                       ON tag_minuman.id = rel_min.product_tag_id
                      AND tag_minuman.name->>'en_US' ILIKE '%minuman%'

                WHERE so.state IN ('draft', 'sale', 'done')
                GROUP BY so.date_order::date
            ),

            /* ==========================================================
               2. AGREGASI PENGELUARAN
               ========================================================== */
            exp_agg AS (
                SELECT
                    peng.tanggal::date AS date,
                    SUM(exp_line.subtotal) AS expense
                FROM pengeluaran_line exp_line
                JOIN pengeluaran_pengeluaran peng
                  ON peng.id = exp_line.pengeluaran_id
                GROUP BY peng.tanggal::date
            )

            /* ==========================================================
               3. GABUNGKAN KEDUANYA  (FULL OUTER JOIN → semua tanggal muncul)
               ========================================================== */
            SELECT
                row_number() OVER ()                      AS id,
                COALESCE(sa.date, ea.date)                AS date,
                COALESCE(sa.komisi,          0)          AS komisi,
                 COALESCE(sa.amount_paket,         0)                             AS amount_paket,
                COALESCE(sa.amount_minuman,       0)                             AS amount_minuman,
                COALESCE(sa.amount_cash,          0)      AS amount_cash,
                COALESCE(sa.amount_debit_mandiri, 0)      AS amount_debit_mandiri,
                COALESCE(sa.amount_debit_bca,     0)      AS amount_debit_bca,
                COALESCE(sa.amount_transfer,      0)      AS amount_transfer,
                COALESCE(sa.amount_qris,          0)      AS amount_qris,

                COALESCE(sa.revenue, 0)                   AS revenue,
                COALESCE(ea.expense, 0)                   AS expense,
                COALESCE(sa.revenue, 0) - COALESCE(ea.expense, 0) AS net
            FROM so_agg sa
            FULL OUTER JOIN exp_agg ea
              ON sa.date = ea.date
              order by sa.date desc
        );
    """)