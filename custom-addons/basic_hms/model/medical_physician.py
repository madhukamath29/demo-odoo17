# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_physician(models.Model):
    _name="medical.physician"
    _description = 'medical physician'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', 'Doctor', required=True)
    institution_partner_id = fields.Many2one('res.partner', domain=[('is_institution', '=', True)],
                                             string='Institution')
    code = fields.Char('Id')
    info = fields.Text('Extra Info')
    doc_id=fields.Many2one(comodel_name='hr.employee')
    # birthday = fields.Date(related='doc_id.birthday', string="DOB", readonly=True)
    specialization = fields.Char(string="Specialization")
    qualifications = fields.Char(string="Qualifications")
    years_exp = fields.Char(string="Years of Experience")
    pro_reg_no = fields.Char(string="Professional Registration Number")
    aff_ins = fields.Char(string="Affiliated Institutions")
    consult_hours = fields.Char(string="Consultation Hours")
    lang_spoken = fields.Char(string="Languages Spoken")
    emp_id = fields.Char(string="Employee ID")
    emg_contact = fields.Char(string="Name of Emergency Contact")
    specialization = fields.Char(string="Specialization")
    identification_proof = fields.Char(string="Identification Proof")
    cons_fees = fields.Float(string="Consultation Fees")
