from odoo import models, fields, api
from datetime import date

class CustomEmployee(models.Model):
    _inherit = 'hr.employee'

    # Add your custom fields here
    emp_id = fields.Char(string="Employee ID")
    date_of_joining = fields.Date(string="Date of Joining")
    age = fields.Integer(string="Age", compute='_compute_age', store=True)
    salary = fields.Float(string="Salary/Compensation")
    emergency_contact_relationship = fields.Char(string="Emergency Contact - Relationship")
    bank_name = fields.Char(string="Bank Name")
    ifsc_code = fields.Char(string="IFSC Code")
    tax_identification_number = fields.Char(string="Tax Identification Number (PAN)")
    health_insurance_enrollment = fields.Boolean(string="Health Insurance Enrollment")
    provident_fund_enrollment = fields.Boolean(string="Provident Fund (PF) Enrollment")
    other_benefits_enrollment = fields.Boolean(string="Other Benefits Enrollment")

    @api.depends('birthday')
    def _compute_age(self):
        for employee in self:
            if employee.birthday:
                today = date.today()
                employee.age = today.year - employee.birthday.year - (
                        (today.month, today.day) < (employee.birthday.month, employee.birthday.day))
            else:
                employee.age = 0
