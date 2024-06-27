from odoo import models, fields

class MedicalForm(models.Model):
    _name = 'medical.form'
    _description = 'Medicine Form Types'

    name = fields.Text('Medicine Form', required=True)

class MedicalForm(models.Model):
    _name = 'medical.administration'
    _description = 'Medicine Route of Adminstration'

    name = fields.Text('Route of Adminstration', required=True)