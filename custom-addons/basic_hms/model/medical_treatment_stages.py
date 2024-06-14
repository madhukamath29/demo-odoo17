from odoo import api, fields, models, _


class medical_treatment_stages(models.Model):
    _name = 'medical.treatment.stages'
    _description = 'Medical Treatment Stages'

    name = fields.Text('Name')
