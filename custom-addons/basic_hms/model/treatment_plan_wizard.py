from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


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


class Project(models.Model):
    _inherit = 'project.project'

    treatment_stages = fields.Many2many('medical.treatment.stages', string='Treatment Stages')


class ProjectTask(models.Model):
    _inherit = 'project.task'

    patient_id = fields.Many2one('medical.patient', string="Patient")
    doctor_id = fields.Many2one('medical.physician', 'Prescribing Doctor')

    product_id = fields.Many2one('product.product', string='Product')
    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials', compute='_compute_bom', store=True)
    quantity = fields.Float(string='Quantity', default=1.0)

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

    # project_task = fields.One2many(, string='stages')
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
        # Check if we are in the context of creating sub-tasks
        if self.env.context.get('creating_sub_tasks'):
            return super(ProjectTask, self).create(vals)

        # Create the main task
        task = super(ProjectTask, self).create(vals)

        # Retrieve the treatment_stages from the related project
        if task.project_id.treatment_stages:
            treatment_stages = task.project_id.treatment_stages
            # Create sub-tasks for each treatment_stage with a context flag to avoid recursion
            for stage in treatment_stages:
                self.with_context(creating_sub_tasks=True).create({
                    'name': stage.name,
                    'parent_id': task.id,
                    'project_id': task.project_id.id,
                })

        return task
