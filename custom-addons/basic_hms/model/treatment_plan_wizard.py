from odoo import models, fields, api
from odoo.exceptions import UserError


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

    product_id = fields.Many2one('product.product', string='Product' )
    bom_id = fields.Many2one('mrp.bom', string='Bill of Materials', compute='_compute_bom', store=True)
    quantity = fields.Float(string='Quantity', default=1.0)

    @api.depends('product_id')
    def _compute_bom(self):
        for record in self:
            if record.product_id:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', record.product_id.product_tmpl_id.id)],
                                                 limit=1)
                record.bom_id = bom if bom else False

    # @api.depends('product_id')
    # # product_id = fields.Many2one('mrp.bom', string='Product')
    # bom_ids = fields.One2many('mrp.bom', 'Product')
    # product_id = fields.One2many('product.product', 'Bill of Material')

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
