# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools
from psycopg2.extensions import AsIs

class MisCash_flow(models.Model):

    _inherit = 'mis.cash_flow'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        auto_join=True,
        index=True,
        readonly=True,
    )

    @api.model_cr
    def init(self):
        account_type_receivable = self.env.ref(
            'account.data_account_type_receivable')
        query = """
            SELECT
                -- we use negative id to avoid duplicates and we don't use
                -- ROW_NUMBER() because the performance was very poor
                -aml.id as id,
                CAST('move_line' AS varchar) as line_type,
                aml.id as move_line_id,
                aml.account_id as account_id,
                CASE
                    WHEN aml.balance > 0
                    THEN aml.balance
                    ELSE 0.0
                END AS debit,
                CASE
                    WHEN aml.balance < 0
                    THEN -aml.balance
                    ELSE 0.0
                END AS credit,
                aml.analytic_account_id as analytic_account_id,
                aml.reconciled as reconciled,
                aml.full_reconcile_id as full_reconcile_id,
                aml.partner_id as partner_id,
                aml.company_id as company_id,
                aml.user_type_id as user_type_id,
                aml.name as name,
                aml.date_maturity as date
            FROM account_move_line as aml
            UNION ALL
            SELECT
                fl.id as id,
                CAST('forecast_line' AS varchar) as line_type,
                Null as move_line_id,
                fl.account_id as account_id,
                CASE
                    WHEN fl.balance > 0
                    THEN fl.balance
                    ELSE 0.0
                END AS debit,
                CASE
                    WHEN fl.balance < 0
                    THEN -fl.balance
                    ELSE 0.0
                END AS credit,
                fl.analytic_account_id as analytic_account_id,
                Null as reconciled,
                Null as full_reconcile_id,
                fl.partner_id as partner_id,
                fl.company_id as company_id,
                %i as user_type_id,
                fl.name as name,
                fl.date as date
            FROM mis_cash_flow_forecast_line as fl
        """ % account_type_receivable.id
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            'CREATE OR REPLACE VIEW %s AS %s',
            (AsIs(self._table), AsIs(query))
        )
