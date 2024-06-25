from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WizardCreateProjectTask(models.TransientModel):
    _name = 'wizard.create.project.task'
    _description = 'Wizard to create a task in a selected project'

    project_id = fields.Many2one('project.project', string="Treatment Type", required=True)
    task_name = fields.Char(string="Patient Name", required=True,
                            default=lambda self: self.env.context.get('default_task_name', ''))
    doctor_name = fields.Char(string="Doctor Name", required=True,
                              default=lambda self: self.env.context.get('default_doctor_name', ''))

    def create_task(self):
        self.ensure_one()
        appointment_id = self.env.context.get('active_id')
        appointment = self.env['medical.appointment'].browse(appointment_id)
        if not appointment:
            return

        task_vals = {
            'name': self.task_name,
            'project_id': self.project_id.id,
            'patient_id': appointment.patient_id.id,
            'appointment_id': appointment.id,
            'doctor_id': appointment.doctor_id.id,  # Assuming appointment has a doctor_id field
        }

        task = self.env['project.task'].create(task_vals)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Project Task',
            'res_model': 'project.task',
            'view_mode': 'form',
            'res_id': task.id,
            'target': 'current',
        }


class Project(models.Model):
    _inherit = 'project.project'

    treatment_stages = fields.Many2many('medical.treatment.stages', string='Treatment Stages')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    patient_id = fields.Many2one('medical.patient', string="Patient")
    doctor_id = fields.Many2one('medical.physician', 'Prescribing Doctor')

    appointment_id = fields.Many2one('medical.appointment', string="Appointment")
    product_id = fields.Many2one('product.product', string='Product')
    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials', compute='_compute_bom', store=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    follow_up_appointments = fields.Date(string="Follow-Up Appointments", store=True)

    @api.depends('product_id')
    def _compute_bom(self):
        for record in self:
            if record.product_id:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)],
                                                 limit=1)
                record.bom_id = bom if bom else False

    def create_manufacturing_order(self):
        self.ensure_one()
        if not self.bom_id:
            raise UserError('No Bill of Materials found for this product.')

        mo_vals = {
            'product_id': self.product_id.id,
            'product_qty': self.quantity,
            'bom_id': self.bom_id.id,
            'product_uom_id': self.product_id.uom_id.id,
        }

        mo = self.env['mrp.production'].create(mo_vals)
        return {
            'name': 'Manufacturing Order',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'res_id': mo.id,
        }

    parent_id = fields.Many2one(
        'project.task',
        string='Parent Task',
        index=True,
        domain="['!', ('id', 'child_of', id)]",
        tracking=True
    )
    child_ids = fields.One2many(
        'project.task',
        'parent_id',
        string="Sub-tasks",
        domain="[('recurring_task', '=', False)]"
    )
    prescription_ids = fields.One2many(
        comodel_name='medical.prescription.order',
        inverse_name='task_id',
        string='Prescriptions'
    )
    all_child_prescription_ids = fields.One2many(
        comodel_name='medical.prescription.order',
        compute='_compute_all_child_prescription_ids',
        string='All Child Prescriptions',
        store=False
    )

    is_subtask = fields.Boolean(string="Is Subtask", compute="_compute_is_subtask", store=True)

    @api.depends('parent_id')
    def _compute_is_subtask(self):
        for task in self:
            task.is_subtask = bool(task.parent_id)

    @api.depends('child_ids.prescription_ids')
    def _compute_all_child_prescription_ids(self):
        for task in self:
            all_prescriptions = self.env['medical.prescription.order']
            for child in task.child_ids:
                all_prescriptions |= child.prescription_ids
            task.all_child_prescription_ids = all_prescriptions

    @api.model
    def create(self, vals):
        if self.env.context.get('creating_sub_tasks'):
            return super(ProjectTask, self).create(vals)

        task = super(ProjectTask, self).create(vals)

        if task.project_id.treatment_stages:
            treatment_stages = task.project_id.treatment_stages
            for stage in treatment_stages:
                self.with_context(creating_sub_tasks=True).create({
                    'name': stage.name,
                    'parent_id': task.id,
                    'project_id': task.project_id.id,
                    'patient_id': task.patient_id.id,
                    'doctor_id': task.doctor_id.id,
                })

        return task
