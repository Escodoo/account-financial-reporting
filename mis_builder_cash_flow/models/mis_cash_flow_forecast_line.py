# Copyright 2019 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MisCashFlowForecastLine(models.Model):

    _name = 'mis.cash_flow.forecast_line'
    _description = 'MIS Cash Flow Forecast Line'

    date = fields.Date(
        required=True,
        index=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        required=True,
        help='The account of the forecast line is only for informative '
        'purpose',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    name = fields.Char(
        required=True,
        default='/',
    )
    balance = fields.Float(
        required=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id.id,
        index=True,
    )

    res_id = fields.Integer(string="Resource ID")
    res_model_id = fields.Many2one('ir.model', 'Document Model', ondelete='cascade')
    res_model = fields.Char('Document Model Name', related='res_model_id.model', readonly=True, store=True)

    parent_res_id = fields.Integer(string="Parent Resource ID")
    parent_res_model_id = fields.Many2one('ir.model', 'Parent Document Model', ondelete='cascade')
    parent_res_model = fields.Char('Parent Document Model Name', related='parent_res_model_id.model', readonly=True, store=True)

    @api.multi
    @api.constrains('company_id', 'account_id')
    def _check_company_id_account_id(self):
        if self.filtered(lambda x: x.company_id != x.account_id.company_id):
            raise ValidationError(_(
                'The Company and the Company of the Account must be the '
                'same.'))

    def action_open_document_related(self):
        if self.res_model and self.res_id:
            return self.env[self.res_model].browse(self.res_id).get_formview_action()
        return False

    def action_open_parent_document_related(self):
        if self.parent_res_model and self.parent_res_id:
            return self.env[self.parent_res_model].browse(self.parent_res_id).get_formview_action()
        return False
