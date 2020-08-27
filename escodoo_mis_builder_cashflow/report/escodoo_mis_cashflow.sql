CREATE OR REPLACE VIEW escodoo_mis_cashflow AS (
    SELECT ROW_NUMBER() OVER() AS id, escodoo_mis_cashflow.* FROM (

        WITH currency_rate as (
            SELECT
              r.currency_id,
              COALESCE(r.company_id, c.id) as company_id,
              r.rate,
              r.name AS date_start,
              (SELECT name FROM res_currency_rate r2
              WHERE r2.name > r.name AND
                    r2.currency_id = r.currency_id AND
                    (r2.company_id is null or r2.company_id = c.id)
               ORDER BY r2.name ASC
               LIMIT 1) AS date_end
            FROM res_currency_rate r
              JOIN res_company c ON (r.company_id is null or r.company_id = c.id)
        )

        /* UNINVOICED PURCHASES */
    SELECT
        CAST('uninvoiced_purchase' AS varchar) AS line_type,
        pol.company_id AS company_id,
        pol.name AS name,
        pol.date_planned::date AS date,
        pol.account_analytic_id AS analytic_account_id,
        pol.partner_id as partner_id,
        pol.id AS res_id,
        'purchase.order.line' AS res_model,
        CASE
          WHEN (cast(split_part(ip.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ip.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipc.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipc.value_reference, ',', 2) AS INTEGER)
          WHEN (cast(split_part(ipd.value_reference, ',', 2) AS INTEGER) IS NOT NULL) THEN cast(split_part(ipd.value_reference, ',', 2) AS INTEGER)
          ELSE cast(NULL AS INTEGER)
        END AS account_id,
        CASE
          WHEN (pol.price_unit / COALESCE(cur.rate, 1.0) * (pol.product_qty - pol.qty_invoiced))::decimal(16,2) >= 0.0 THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (pol.price_unit / COALESCE(cur.rate, 1.0) * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)  < 0 THEN (pol.price_unit / COALESCE(cur.rate, 1.0) * (pol.product_qty - pol.qty_invoiced))::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM purchase_order_line pol
            LEFT JOIN purchase_order po on po.id = pol.order_id
            LEFT JOIN product_product pp ON pp.id = pol.product_id
            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc ON pc.id = pt.categ_id
            LEFT JOIN ir_property ip ON ip.name = 'property_account_expense_id' AND ip.type='many2one' AND ip.res_id ='product.template,' || pt.id
            LEFT JOIN ir_property ipc ON ipc.name = 'property_account_expense_categ_id' AND ipc.type='many2one' AND ipc.res_id ='product.category,' || pc.id
            LEFT JOIN ir_property ipd ON ipd.name = 'property_account_expense_categ_id' AND ipd.type='many2one' AND (ipd.res_id IS NULL OR ipd.res_id = '')
            LEFT JOIN currency_rate cur on (cur.currency_id = po.currency_id and
                cur.company_id = po.company_id and
                cur.date_start <= coalesce(po.date_order, now()) and
                (cur.date_end is null or cur.date_end > coalesce(po.date_order, now())))
        WHERE pol.product_qty > pol.qty_invoiced AND po.state != 'cancel' AND po.state != 'draft'

    UNION ALL

        /* DRAFT IN INVOICES */
    SELECT
        CAST('draft_in_invoice' AS varchar) AS line_type,
        ail.company_id AS company_id,
        ail.name AS name,
        ail.create_date::date as date,
        ail.account_analytic_id as analytic_account_id,
        ail.partner_id as partner_id,
        ail.id AS res_id,
        'account.invoice.line' AS res_model,
        ail.account_id as account_id,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2) >= 0.0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)  < 0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM account_invoice_line ail
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN currency_rate cur on (cur.currency_id = ai.currency_id and
                cur.company_id = ai.company_id and
                cur.date_start <= coalesce(ai.date_invoice, now()) and
                (cur.date_end is null or cur.date_end > coalesce(ai.date_invoice, now())))
        WHERE ai.state = 'draft' AND ai.type IN ('in_invoice', 'out_refund')

    UNION ALL

        /* DRAFT OUT INVOICES */
    SELECT
        CAST('draft_out_invoice' AS varchar) AS line_type,
        ail.company_id AS company_id,
        ail.name AS name,
        ail.create_date::date as date,
        ail.account_analytic_id as analytic_account_id,
        ail.partner_id as partner_id,
        ail.id AS res_id,
        'account.invoice.line' AS res_model,
        ail.account_id as account_id,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)  < 0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2) >= 0.0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM account_invoice_line ail
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN currency_rate cur on (cur.currency_id = ai.currency_id and
                cur.company_id = ai.company_id and
                cur.date_start <= coalesce(ai.date_invoice, now()) and
                (cur.date_end is null or cur.date_end > coalesce(ai.date_invoice, now())))
        WHERE ai.state = 'draft' AND ai.type IN ('out_invoice', 'in_refund')

    UNION ALL

        /* IN INVOICES */
    SELECT
        CAST('in_invoice' AS varchar) AS line_type,
        ail.company_id AS company_id,
        ail.name AS name,
        ail.create_date::date as date,
        ail.account_analytic_id as analytic_account_id,
        ail.partner_id as partner_id,
        ail.id AS res_id,
        'account.invoice.line' AS res_model,
        ail.account_id as account_id,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2) >= 0.0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)  < 0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM account_invoice_line ail
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN currency_rate cur on (cur.currency_id = ai.currency_id and
                cur.company_id = ai.company_id and
                cur.date_start <= coalesce(ai.date_invoice, now()) and
                (cur.date_end is null or cur.date_end > coalesce(ai.date_invoice, now())))
        WHERE ai.state = 'open' AND ai.type IN ('in_invoice', 'out_refund')

    UNION ALL

        /* OUT INVOICES */
    SELECT
        CAST('out_invoice' AS varchar) AS line_type,
        ail.company_id AS company_id,
        ail.name AS name,
        ail.create_date::date as date,
        ail.account_analytic_id as analytic_account_id,
        ail.partner_id as partner_id,
        ail.id AS res_id,
        'account.invoice.line' AS res_model,
        ail.account_id as account_id,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)  < 0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS debit,
        CASE
          WHEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2) >= 0.0 THEN (ail.price_subtotal / COALESCE(cur.rate, 1.0))::decimal(16,2)
          ELSE 0.0
        END AS credit
        FROM account_invoice_line ail
            LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
            LEFT JOIN currency_rate cur on (cur.currency_id = ai.currency_id and
                cur.company_id = ai.company_id and
                cur.date_start <= coalesce(ai.date_invoice, now()) and
                (cur.date_end is null or cur.date_end > coalesce(ai.date_invoice, now())))
        WHERE ai.state = 'open' AND ai.type IN ('out_invoice', 'in_refund')

--    /* MOVE LINE */
--
--    SELECT
--        CAST('move_line' AS varchar) as line_type,
--        aml.company_id as company_id,
--        aml.name as name,
--        aml.date_maturity::date as date,
--        aml.analytic_account_id as analytic_account_id,
--        aml.partner_id as partner_id,
--        aml.id AS res_id,
--        'account.move.line' AS res_model,
--        aml.account_id as account_id,
--        CASE
--            WHEN aml.balance > 0
--            THEN aml.balance
--            ELSE 0.0
--        END AS debit,
--        CASE
--            WHEN aml.balance < 0
--            THEN -aml.balance
--            ELSE 0.0
--        END AS credit
--    FROM account_move_line as aml

    ) AS escodoo_mis_cashflow
)
