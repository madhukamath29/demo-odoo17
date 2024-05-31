from odoo import models, fields, api


class WizardCreateProjectTask(models.TransientModel):
    _name = 'wizard.create.project.task'
    _description = 'Wizard to create a task in a selected project'

    project_id = fields.Many2one('project.project', string="Treatment Type", required=True)
    task_name = fields.Char(string="Patient Name", required=True,
                            default=lambda self: self.env.context.get('default_task_name', ''))

    def create_task(self):
        self.ensure_one()
        patient_id = self.env.context.get('active_id')
        patient = self.env['medical.patient'].browse(patient_id)
        if not patient:
            return

        task = self.env['project.task'].create({
            'name': self.task_name,
            'project_id': self.project_id.id,
            'patient_id': patient.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project',
            'res_model': 'project.project',
            'view_mode': 'form',
            'res_id': self.project_id.id,
            'target': 'current',
        }


class ProjectTask(models.Model):
    _inherit = 'project.task'

    patient_id = fields.Many2one('medical.patient', string="Patient")
    doctor_id = fields.Many2one('medical.physician', 'Prescribing Doctor')
