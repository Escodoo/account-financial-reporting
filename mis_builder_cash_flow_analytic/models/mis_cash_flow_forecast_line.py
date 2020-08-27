# Copyright 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MisCash_flowForecast_line(models.Model):

    _inherit = 'mis.cash_flow.forecast_line'

    # analytic_account_id = fields.Many2one(
    #     comodel_name='account.analytic.account',
    #     string='Analytic Account',
    #     help='The analytic account of the forecast line is only for informative '
    #     'purpose',
    # )

    # @api.multi
    # @api.constrains('company_id', 'analytic_account_id')
    # def _check_company_id_account_id(self):
    #     if self.filtered(lambda x: x.company_id != x.analytic_account_id.company_id):
    #         raise ValidationError(_(
    #             'The Company and the Company of the Analytic Account must be the '
    #             'same.'))
