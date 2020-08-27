# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
from os.path import join as opj

from odoo import api, fields, models, tools


class EscodooMisCashflow(models.Model):

    _name = 'escodoo.mis.cashflow'
    _description = 'Escodoo Mis Cashflow'
    _auto = False

    line_type = fields.Selection(
        [
            ('uninvoiced_purchase', 'Uninvoiced Purchase'),
            ('draft_in_invoice', 'Draft In Invoice'),
            ('draft_out_invoice', 'Draft Out Invoice'),
            ('move_line', 'Journal Item'),
            ('in_invoice', 'In Invoice'),
            ('out_invoice', 'Out Invoice'),
        ],
        index=True,
        readonly=True,
    )
    name = fields.Char(
        readonly=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        auto_join=True,
        index=True,
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        auto_join=True,
        index=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        auto_join=True,
        readonly=True,
        index=True,
    )
    # move_line_id = fields.Many2one(
    #     comodel_name='account.move.line',
    #     string='Journal Item',
    #     auto_join=True,
    #     readonly=True,
    # )
    credit = fields.Float(
        readonly=True,
    )
    debit = fields.Float(
        readonly=True,
    )
    date = fields.Date(
        readonly=True,
        index=True,
    )
    # reconciled = fields.Boolean(
    #     readonly=True,
    # )
    # full_reconcile_id = fields.Many2one(
    #     'account.full.reconcile',
    #     string="Matching Number",
    #     readonly=True,
    #     index=True,
    # )
    # user_type_id = fields.Many2one(
    #     'account.account.type',
    #     auto_join=True,
    #     readonly=True,
    #     index=True,
    # )


    # resource can be purchase.order.line or account.invoice.line
    res_id = fields.Integer(string="Resource ID")
    res_model = fields.Char(string="Resource Model Name")

    analytic_tag_ids = fields.Many2many(
        comodel_name="account.analytic.tag",
        relation="escodoo_mis_cashflow_tag_rel",
        column1="escodoo_mis_cashflow_id",
        column2="account_analytic_tag_id",
        string="Analytic Tags",
    )

    @api.model_cr
    def init(self):
        script = opj(os.path.dirname(__file__), "escodoo_mis_cashflow.sql")
        with open(script) as f:
            tools.drop_view_if_exists(self.env.cr, "escodoo_mis_cashflow")
            self.env.cr.execute(f.read())

            # Create many2many relation for account.analytic.tag
            tools.drop_view_if_exists(self.env.cr, "escodoo_mis_cashflow_tag_rel")
            self.env.cr.execute(
                """
            CREATE OR REPLACE VIEW escodoo_mis_cashflow_tag_rel AS
            (SELECT
                po_mcp.id AS escodoo_mis_cashflow_id,
                po_rel.account_analytic_tag_id AS account_analytic_tag_id
            FROM account_analytic_tag_purchase_order_line_rel AS po_rel
            INNER JOIN escodoo_mis_cashflow AS po_mcp ON
                po_mcp.res_id = po_rel.purchase_order_line_id
            WHERE po_mcp.res_model = 'purchase.order.line'
            UNION ALL
            SELECT
                inv_mcp.id AS escodoo_mis_cashflow_id,
                inv_rel.account_analytic_tag_id AS account_analytic_tag_id
            FROM account_analytic_tag_account_invoice_line_rel AS inv_rel
            INNER JOIN escodoo_mis_cashflow AS inv_mcp ON
                inv_mcp.res_id = inv_rel.account_invoice_line_id
            WHERE inv_mcp.res_model = 'account.invoice.line')
            """
            )
