# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class medical_prescription_order(models.Model):
    _name = "medical.prescription.order"
    _description = 'medical Prescription order'

    name = fields.Char('Prescription ID')
    patient_id = fields.Many2one(
        comodel_name='medical.patient',
        string='Patient Name',
        required=True
    )
    prescription_date = fields.Datetime('Prescription Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Login User', readonly=True, default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.move', 'Invoice')
    invoice_to_insurer = fields.Boolean('Invoice to Insurance')
    doctor_id = fields.Many2one('medical.physician', 'Doctor Name')
    medical_appointment_id = fields.Many2one('medical.appointment', 'Appointment')
    state = fields.Selection([('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    pharmacy_partner_id = fields.Many2one('res.partner', domain=[('is_pharmacy', '=', True)], string='Pharmacy')
    prescription_line_ids = fields.One2many('medical.prescription.line', 'name', 'Prescription Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    appointment_id = fields.Many2one('medical.appointment', string="Appointment")
    is_invoiced = fields.Boolean(copy=False, default=False)
    insurer_id = fields.Many2one('medical.insurance', 'Insurer')
    is_shipped = fields.Boolean(default=False, copy=False)
    contact_number = fields.Char('Pharmacy Contact Information')

    height = fields.Float(related='patient_id.height', string="Height", readonly=True)
    weight = fields.Float(related='patient_id.weight', string="Weight", readonly=True)
    ph_no = fields.Char(related='patient_id.ph_no', string="Phone Number", readonly=True)
    # diagnosis = fields.Char(related='patient_id.diagnosis', string="Diagnosis", readonly=True)
    diagnosis = fields.Char(string="Diagnosis")
    allergies = fields.Char(related='patient_id.allergies', string="Allergies", readonly=True)
    general_info = fields.Text(related='patient_id.general_info', string="Patient Instruction", readonly=True)
    followUp_date = fields.Date(related='patient_id.followUp_date', string="Follow-Up Appointments", store=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('medical.prescription.order') or '/'
        return super(medical_prescription_order, self).create(vals_list)

    def prescription_report(self):
        return self.env.ref('basic_hms.report_print_prescription').report_action(self)

    @api.onchange('name')
    def onchange_name(self):
        ins_obj = self.env['medical.insurance']
        ins_record = ins_obj.search([('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
        self.insurer_id = ins_record.id or False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
