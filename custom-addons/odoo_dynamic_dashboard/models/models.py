# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HrEmployeeSkillReport(models.Model):
    _name = 'hr.employee.skill.report'
    _description = 'Employee Skills Report'
    _order = 'employee_id, level_progress desc'

    employee_id = fields.Many2one('hr.employee', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    department_id = fields.Many2one('hr.department', readonly=True)
    skill_id = fields.Many2one('hr.skill', readonly=True)
    skill_type_id = fields.Many2one('hr.skill.type', readonly=True)
    skill_level = fields.Char(readonly=True)
    level_progress = fields.Float(readonly=True, group_operator='avg')
