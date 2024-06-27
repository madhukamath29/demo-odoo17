# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class MedicalPrescriptionLine(models.Model):
    _name = "medical.prescription.line"
    _description = 'medical prescription line'

    name = fields.Many2one('medical.prescription.order', 'Prescription ID')
    medicament_id = fields.Many2one('medical.medicament', 'Medication Name')
    indication = fields.Char('Indication')
    allow_substitution = fields.Boolean('Allow Substitution')
    forme = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route = fields.Char('Route of Administration')
    end_treatement = fields.Datetime('Administration Route')
    dose = fields.Float('Dosage Form')
    dose_unit_id = fields.Many2one('medical.dose.unit', 'Dose Unit')
    qty = fields.Integer('Strength')
    medication_dosage_id = fields.Many2one('medical.medication.dosage', 'Frequency')
    admin_times = fields.Char('Admin Hours', size=128)
    frequency = fields.Integer('Frequency No')
    frequency_unit = fields.Selection(
        [('seconds', 'Seconds'), ('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), ('weeks', 'Weeks'),
         ('wr', 'When Required')], 'Unit')
    duration = fields.Integer('Treatment Duration')
    duration_period = fields.Selection(
        [('minutes', 'Minutes'), ('hours', 'hours'), ('days', 'Days'), ('months', 'Months'), ('years', 'Years'),
         ('indefine', 'Indefine')], 'Treatment Period')
    quantity = fields.Integer('Quantity Prescribed')
    review = fields.Datetime('Review Date')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Dosage Instructions', size=128)
    end_treatment = fields.Datetime('End of treatment')
    start_treatment = fields.Datetime('Start of treatment')
    instructions = fields.Char('Special Instructions')
    patient_id = fields.Many2one('medical.patient', string="Patient", compute='_compute_patient_id', store=True)
    form_id = fields.Many2one('medical.form', string="Medical Form")
    admin_id = fields.Many2one('medical.administration', string="Medical Route of Administration")

    @api.depends('name')
    def _compute_patient_id(self):
        for record in self:
            record.patient_id = record.name.patient_id

    @api.model
    def create(self, vals):
        # Automatically set patient_id based on the prescription order
        if 'name' in vals:
            prescription_order = self.env['medical.prescription.order'].browse(vals['name'])
            if prescription_order:
                vals['patient_id'] = prescription_order.patient_id.id
        return super(MedicalPrescriptionLine, self).create(vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
