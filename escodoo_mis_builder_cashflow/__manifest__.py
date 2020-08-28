# Copyright 2020 - TODAY, Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Escodoo Mis Builder Cashflow',
    'summary': """
        Escodoo Cashflow""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Escodoo,Odoo Community Association (OCA)',
    'website': 'https://www.escodoo.com.br',
    "depends": ["mis_builder_budget", "purchase", "web_timeline"],

    'data': [
        "templates/assets.xml",
        'security/escodoo_mis_cashflow.xml',
        'report/escodoo_mis_cashflow.xml',
        "data/mis_report_style.xml",
        "data/mis_report.xml",
        "data/mis_budget.xml",
        "data/mis_report_instance.xml",
    ],
    'demo': [
    ],
}
