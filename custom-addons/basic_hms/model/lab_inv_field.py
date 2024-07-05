from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_lab_invoice = fields.Boolean(string='Is Lab Invoice', default=False)
    lab_name = fields.Many2one('medical.lab', string='Lab Name')
    test_id = fields.Many2one('medical.test_type', 'Test Type')
