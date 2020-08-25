# Copyright 2020 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Mis Builder Cash Flow Analytic',
    'summary': """
        Add Analytic Account on MIS Cash Flow""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/mis-builder',
    'depends': [
        'mis_builder_cash_flow',
    ],
    'data': [
        'report/mis_cash_flow.xml',
        'views/mis_cash_flow_forecast_line.xml',
    ],
    'demo': [
        'demo/mis_cash_flow_forecast_line.xml',
    ],
}
