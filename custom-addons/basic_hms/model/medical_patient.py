# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError


class medical_patient(models.Model):
    _name = 'medical.patient'
    _description = 'medical patient'
    _rec_name = 'patient_id'

    @api.onchange('patient_id')
    def _onchange_patient(self):
        '''
        The purpose of the method is to define a domain for the available
        purchase orders.
        '''
        address_id = self.patient_id
        self.partner_address_id = address_id

    def print_report(self):
        return self.env.ref('basic_hms.report_print_patient_card').report_action(self)

    @api.depends('date_of_birth')
    def onchange_age(self):
        for rec in self:
            if rec.date_of_birth:
                d1 = rec.date_of_birth
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                rec.age = str(rd.years) + "y" + " " + str(rd.months) + "m" + " " + str(rd.days) + "d"
            else:
                rec.age = "No Date Of Birth!!"

    patient_id = fields.Many2one('res.partner', domain=[('is_patient', '=', True)], string="Patient", required=True)
    name = fields.Char(string='Id', readonly=True)
    last_name = fields.Char('Last name')
    date_of_birth = fields.Date(string="Date of Birth")
    sex = fields.Selection([('m', 'Male'), ('f', 'Female')], string="Sex")
    age = fields.Char(compute=onchange_age, string="Patient Age", store=True)
    critical_info = fields.Text(string="Patient Critical Information")
    photo = fields.Binary(string="Picture")
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], string="Blood Type")
    rh = fields.Selection([('-+', '+'), ('--', '-')], string="Rh")
    marital_status = fields.Selection(
        [('s', 'Single'), ('m', 'Married'), ('w', 'Widowed'), ('d', 'Divorced'), ('x', 'Seperated')],
        string='Marital Status')
    deceased = fields.Boolean(string='Deceased')
    date_of_death = fields.Date(string="Date of Death")
    cause_of_death = fields.Char(string='Cause of Death')
    receivable = fields.Float(string="Receivable", readonly=True)
    current_insurance_id = fields.Many2one('medical.insurance', string="Insurance")
    partner_address_id = fields.Many2one('res.partner', string="Address", )

    occupation = fields.Char(string="Occupation", )
    # govt_id = fields.Char(string="Identification Proof",)
    govt_id_type = fields.Selection([
        ('aadhar', 'Aadhar Card'),
        ('driving', 'Driving Licence'),
        ('election', 'Election Card')
    ], string="Identification Proof Type")

    govt_id = fields.Char(string="Identification No:", )

    emergency_no = fields.Char(string="Phone Number", )
    relation_patient = fields.Char(string="Relationship to the patient")
    relation_name = fields.Char(string="Name")

    height = fields.Float(string="Height", )
    weight = fields.Float(string="Weight", )
    mobile = fields.Char(related='patient_id.mobile', readonly=False, string="Mobile")
    # diagnosis = fields.Char(string="Diagnosis", )
    allergies = fields.Char(string="Allergies")
    followUp_date = fields.Date(string="Follow-Up Appointments")
    street = fields.Char(related='patient_id.street', readonly=False)
    street2 = fields.Char(related='patient_id.street2', readonly=False)
    zip_code = fields.Char(related='patient_id.zip', readonly=False)
    city = fields.Char(related='patient_id.city', readonly=False)
    state_id = fields.Many2one("res.country.state", related='patient_id.state_id', readonly=False)
    country_id = fields.Many2one('res.country', related='patient_id.country_id', readonly=False)

    primary_care_physician_id = fields.Many2one('medical.physician', string="Primary Care Doctor")
    patient_status = fields.Char(string="Hospitalization Status", readonly=True)
    patient_disease_ids = fields.One2many('medical.patient.disease', 'patient_id')
    patient_psc_ids = fields.One2many('medical.patient.psc', 'patient_id')
    excercise = fields.Boolean(string='Excercise')
    excercise_minutes_day = fields.Integer(string="Minutes/Day")
    sleep_hours = fields.Integer(string="Hours of sleep")
    sleep_during_daytime = fields.Boolean(string="Sleep at daytime")
    number_of_meals = fields.Integer(string="Meals per day")
    coffee = fields.Boolean('Coffee')
    coffee_cups = fields.Integer(string='Cups Per Day')
    eats_alone = fields.Boolean(string="Eats alone")
    soft_drinks = fields.Boolean(string="Soft drinks(sugar)")
    salt = fields.Boolean(string="Salt")
    diet = fields.Boolean(string=" Currently on a diet ")
    diet_info = fields.Integer(string=' Diet info ')
    general_info = fields.Text(string="Info")
    lifestyle_info = fields.Text('Lifestyle Information')
    smoking = fields.Boolean(string="Smokes")
    smoking_number = fields.Integer(string="Cigarretes a day")
    ex_smoker = fields.Boolean(string="Ex-smoker")
    second_hand_smoker = fields.Boolean(string="Passive smoker")
    age_start_smoking = fields.Integer(string="Age started to smoke")
    age_quit_smoking = fields.Integer(string="Age of quitting")
    drug_usage = fields.Boolean(string='Drug Habits')
    drug_iv = fields.Boolean(string='IV drug user')
    ex_drug_addict = fields.Boolean(string='Ex drug addict')
    age_start_drugs = fields.Integer(string='Age started drugs')
    age_quit_drugs = fields.Integer(string="Age quit drugs")
    alcohol = fields.Boolean(string="Drinks Alcohol")
    ex_alcohol = fields.Boolean(string="Ex alcoholic")
    age_start_drinking = fields.Integer(string="Age started to drink")
    age_quit_drinking = fields.Integer(string="Age quit drinking")
    alcohol_beer_number = fields.Integer(string="Beer / day")
    alcohol_wine_number = fields.Integer(string="Wine / day")
    alcohol_liquor_number = fields.Integer(string="Liquor / day")
    cage_ids = fields.One2many('medical.patient.cage', 'patient_id')
    sex_oral = fields.Selection([('0', 'None'),
                                 ('1', 'Active'),
                                 ('2', 'Passive'),
                                 ('3', 'Both')], string='Oral Sex')
    sex_anal = fields.Selection([('0', 'None'),
                                 ('1', 'Active'),
                                 ('2', 'Passive'),
                                 ('3', 'Both')], string='Anal Sex')
    prostitute = fields.Boolean(string='Prostitute')
    sex_with_prostitutes = fields.Boolean(string=' Sex with prostitutes ')
    sexual_preferences = fields.Selection([
        ('h', 'Heterosexual'),
        ('g', 'Homosexual'),
        ('b', 'Bisexual'),
        ('t', 'Transexual'),
    ], 'Sexual Orientation', sort=False)
    sexual_practices = fields.Selection([
        ('s', 'Safe / Protected sex'),
        ('r', 'Risky / Unprotected sex'),
    ], 'Sexual Practices', sort=False)
    sexual_partners = fields.Selection([
        ('m', 'Monogamous'),
        ('t', 'Polygamous'),
    ], 'Sexual Partners', sort=False)
    sexual_partners_number = fields.Integer('Number of sexual partners')
    first_sexual_encounter = fields.Integer('Age first sexual encounter')
    anticonceptive = fields.Selection([
        ('0', 'None'),
        ('1', 'Pill / Minipill'),
        ('2', 'Male condom'),
        ('3', 'Vasectomy'),
        ('4', 'Female sterilisation'),
        ('5', 'Intra-uterine device'),
        ('6', 'Withdrawal method'),
        ('7', 'Fertility cycle awareness'),
        ('8', 'Contraceptive injection'),
        ('9', 'Skin Patch'),
        ('10', 'Female condom'),
    ], 'Anticonceptive Method', sort=False)
    sexuality_info = fields.Text('Extra Information')
    motorcycle_rider = fields.Boolean('Motorcycle Rider', help="The patient rides motorcycles")
    helmet = fields.Boolean('Uses helmet', help="The patient uses the proper motorcycle helmet")
    traffic_laws = fields.Boolean('Obeys Traffic Laws', help="Check if the patient is a safe driver")
    car_revision = fields.Boolean('Car Revision', help="Maintain the vehicle. Do periodical checks - tires,breaks ...")
    car_seat_belt = fields.Boolean('Seat belt', help="Safety measures when driving : safety belt")
    car_child_safety = fields.Boolean('Car Child Safety',
                                      help="Safety measures when driving : child seats, proper seat belting, not seating on the front seat, ....")
    home_safety = fields.Boolean('Home safety',
                                 help="Keep safety measures for kids in the kitchen, correct storage of chemicals, ...")
    fertile = fields.Boolean('Fertile')
    menarche = fields.Integer('Menarche Age')
    menopausal = fields.Boolean('Menopausal')
    menopause = fields.Integer('Menopause age')
    menstrual_history_ids = fields.One2many('medical.patient.menstrual.history', 'patient_id')
    breast_self_examination = fields.Boolean('Breast self-examination')
    mammography = fields.Boolean('Mammography')
    pap_test = fields.Boolean('PAP test')
    last_pap_test = fields.Date('Last PAP test')
    colposcopy = fields.Boolean('Colposcopy')
    mammography_history_ids = fields.One2many('medical.patient.mammography.history', 'patient_id')
    pap_history_ids = fields.One2many('medical.patient.pap.history', 'patient_id')
    colposcopy_history_ids = fields.One2many('medical.patient.colposcopy.history', 'patient_id')
    pregnancies = fields.Integer('Pregnancies')
    premature = fields.Integer('Premature')
    stillbirths = fields.Integer('Stillbirths')
    abortions = fields.Integer('Abortions')
    pregnancy_history_ids = fields.One2many('medical.patient.pregnency', 'patient_id')
    family_history_ids = fields.Many2many('medical.family.disease', string="Family Disease Lines")
    perinatal_ids = fields.Many2many('medical.preinatal')
    ex_alcoholic = fields.Boolean('Ex Alcoholic')
    currently_pregnant = fields.Boolean('Currently Pregnant')
    born_alive = fields.Integer('Born Alive')
    gpa = fields.Char('GPA')
    works_at_home = fields.Boolean('Works At Home')
    colposcopy_last = fields.Date('Last colposcopy')
    mammography_last = fields.Date('Last mammography')
    ses = fields.Selection([
        ('None', ''),
        ('0', 'Lower'),
        ('1', 'Lower-middle'),
        ('2', 'Middle'),
        ('3', 'Middle-upper'),
        ('4', 'Higher'),
    ], 'Socioeconomics', help="SES - Socioeconomic Status", sort=False)
    education = fields.Selection([('o', 'None'), ('1', 'Incomplete Primary School'),
                                  ('2', 'Primary School'),
                                  ('3', 'Incomplete Secondary School'),
                                  ('4', 'Secondary School'),
                                  ('5', 'University')], string='Education Level')
    housing = fields.Selection([
        ('None', ''),
        ('0', 'Shanty, deficient sanitary conditions'),
        ('1', 'Small, crowded but with good sanitary conditions'),
        ('2', 'Comfortable and good sanitary conditions'),
        ('3', 'Roomy and excellent sanitary conditions'),
        ('4', 'Luxury and excellent sanitary conditions'),
    ], 'Housing conditions', help="Housing and sanitary living conditions", sort=False)
    works = fields.Boolean('Works')
    hours_outside = fields.Integer('Hours outside home',
                                   help="Number of hours a day the patient spend outside the house")
    hostile_area = fields.Boolean('Hostile Area')
    notes = fields.Text(string="Extra info")
    sewers = fields.Boolean('Sanitary Sewers')
    water = fields.Boolean('Running Water')
    trash = fields.Boolean('Trash recollection')
    electricity = fields.Boolean('Electrical supply')
    gas = fields.Boolean('Gas supply')
    telephone = fields.Boolean('Telephone')
    television = fields.Boolean('Television')
    internet = fields.Boolean('Internet')
    single_parent = fields.Boolean('Single parent family')
    domestic_violence = fields.Boolean('Domestic violence')
    working_children = fields.Boolean('Working children')
    teenage_pregnancy = fields.Boolean('Teenage pregnancy')
    sexual_abuse = fields.Boolean('Sexual abuse')
    drug_addiction = fields.Boolean('Drug addiction')
    school_withdrawal = fields.Boolean('School withdrawal')
    prison_past = fields.Boolean('Has been in prison')
    prison_current = fields.Boolean('Is currently in prison')
    relative_in_prison = fields.Boolean('Relative in prison',
                                        help="Check if someone from the nuclear family - parents sibblings  is or has been in prison")
    fam_apgar_help = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Help from family',
        help="Is the patient satisfied with the level of help coming from the family when there is a problem ?",
        sort=False)
    fam_apgar_discussion = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Problems discussion',
        help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Decision making',
        help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Time sharing',
        help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Family affection',
        help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    fam_apgar_score = fields.Integer('Score',
                                     help="Total Family APGAR 7 - 10 : Functional Family 4 - 6  : Some level of disfunction \n"
                                          "0 - 3  : Severe disfunctional family \n")
    lab_test_ids = fields.One2many('medical.patient.lab.test', 'patient_id')
    fertile = fields.Boolean('Fertile')
    menarche_age = fields.Integer('Menarche age')
    menopausal = fields.Boolean('Menopausal')
    pap_test_last = fields.Date('Last PAP Test')
    colposcopy = fields.Boolean('Colpscopy')
    gravida = fields.Integer('Pregnancy')
    medical_vaccination_ids = fields.One2many('medical.vaccination', 'medical_patient_vaccines_id')
    medical_appointments_ids = fields.One2many('medical.appointment', 'patient_id', string='Appointments')
    lastname = fields.Char('Last Name')
    report_date = fields.Date('Date', default=datetime.today().date())
    medication_ids = fields.One2many('medical.patient.medication1', 'medical_patient_medication_id')

    deaths_2nd_week = fields.Integer('Deceased after 2nd week')
    deaths_1st_week = fields.Integer('Deceased after 1st week')
    full_term = fields.Integer('Full Term')
    ses_notes = fields.Text('Notes')
    treatment_plan_ids = fields.One2many('project.task', 'patient_id', string='Treatment Plans')
    prescription_line_id = fields.One2many('medical.prescription.line', 'patient_id', string="Prescription Line")
    language_preferences = fields.Char(string="Language Preferences")
    preferred_appointment_times = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
    ], string="Preferred Appointment Times")
    special_needs_or_disabilities = fields.Char(string="Special Needs or Disabilities")
    anxiety_or_phobia_information = fields.Char(string="Anxiety or Phobia Information")
    recall_reminders_method = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call')
    ], string="Recall Reminders Method")
    recall_reminders_frequency = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string="Recall Reminders Frequency")
    oral_hygiene_practices = fields.Char(string="Oral Hygiene Practices")
    email_address = fields.Char(string="Email Address")
    family_med_history = fields.Char(string="Family Medical History")
    diet_hab = fields.Char(string="Dietary Habits")
    pay_method_pref = fields.Selection([
        ('debit_card', 'Debit Card'),
        ('credit_card', 'Credit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash')
    ], string="Payment Method Preference")
    # treatment_consent = fields.Boolean(string="Treatment Consent")

    treatment_consent = fields.Boolean(string="Treatment Consent")
    treatment_consent_label = fields.Char(string="", compute='_compute_treatment_consent_label')
    tooth_ids = fields.One2many('medical.tooth', inverse_name='patient_id', compute='_compute_tooth_details',
                                string='Tooth', readonly=True)

    # all_child_tooth_ids = fields.One2many('medical.tooth', 'patient_id', string="Prescription Line")
    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')

    @api.depends('appointment_ids.tooth_ids')
    def _compute_tooth_details(self):

        for patient in self:
            tooth_details = self.env['medical.tooth'].search([('patient_id', '=', patient.id)])
            patient.tooth_ids = [(6, 0, tooth_details.ids)]

    @api.depends('treatment_consent')
    def _compute_treatment_consent_label(self):
        for record in self:
            record.treatment_consent_label = "Yes" if record.treatment_consent else "No"

    # @api.onchange('govt_id_type')
    # def _onchange_govt_id_type(self):
    #     if self.govt_id_type:
    #         self.govt_id = ''  # Reset the ID field when type changes
    #     else:
    #         self.govt_id = False  # Clear the ID field if no type is selected

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            appointment = self._context.get('appointment_id')
            res_partner_obj = self.env['res.partner']
            if appointment:
                val_1 = {'name': self.env['res.partner'].browse(val['patient_id']).name}
                patient = res_partner_obj.create(val_1)
                val.update({'patient_id': patient.id})
            if val.get('date_of_birth'):
                dt = val.get('date_of_birth')
                d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
                d2 = datetime.today().date()
                rd = relativedelta(d2, d1)
                age = str(rd.years) + "y" + " " + str(rd.months) + "m" + " " + str(rd.days) + "d"
                val.update({'age': age})

            patient_id = self.env['ir.sequence'].next_by_code('medical.patient')
            if patient_id:
                val.update({
                    'name': patient_id,
                })

        return super(medical_patient, self).create(vals_list)

    @api.constrains('date_of_death')
    def _check_date_death(self):
        for rec in self:
            if rec.date_of_birth:
                if rec.deceased == True:
                    if rec.date_of_death <= rec.date_of_birth:
                        raise UserError(_('Date Of Death Can Not Less Than Date Of Birth.'))

                    class PrescriptionLine(models.Model):
                        _inherit = 'medical.prescription.line'

                        @api.model
                        def unlink(self):
                            # Get the related medication IDs
                            medication_ids = self.mapped('medicament_id')

                            # Perform the unlink operation
                            result = super(PrescriptionLine, self).unlink()

                            # Check if any medication does not have related prescription lines anymore
                            for medication in medication_ids:
                                if not medication.prescription_line_id:
                                    medication.unlink()

                            return result

    def copy(self, default=None):
        for rec in self:
            raise UserError(_('You Can Not Duplicate Patient.'))

    def action_view_prescriptions(self):
        return {
            'name': _('Prescription Orders'),
            'domain': [('patient_id', '=', self.id)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'medical.prescription.order',
            'type': 'ir.actions.act_window',
            'context': {'default_patient_id': self.id},
        }

    # def action_create_project_task(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Create Task in Project',
    #         'res_model': 'wizard.create.project.task',
    #         'view_mode': 'form',
    #         'view_id': self.env.ref('basic_hms.view_wizard_create_project_task').id,
    #         'target': 'new',
    #         'context': {
    #             'default_task_name': self.patient_id.name,
    #         },
    #     }

    def action_view_patient_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'project.task',
            'view_mode': 'kanban,tree,form',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    task_count = fields.Integer(string="Task Count", compute='_compute_task_count')

    def _compute_task_count(self):
        for patient in self:
            patient.task_count = self.env['project.task'].search_count([('patient_id', '=', patient.id)])

    prescription_ids = fields.One2many(
        comodel_name='medical.prescription.order',
        inverse_name='patient_id',
        string='Prescriptions',
        readonly='True'
    )
    appointment_ids = fields.One2many('medical.appointment', 'patient_id', string='Appointments')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count', store=True)

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for patient in self:
            patient.appointment_count = len(patient.appointment_ids)

    def action_create_appointment(self):
        appointment_values = {
            'patient_id': self.id,
        }
        appointment = self.env['medical.appointment'].create(appointment_values)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Appointment',
            'res_model': 'medical.appointment',
            'res_id': appointment.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

    def action_view_appointment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointment',
            'res_model': 'medical.appointment',
            'view_mode': 'list',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},

        }

    def action_view_tooth_report(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tooth Report',
            'res_model': 'medical.appointment',
            'view_mode': 'list',
            'domain': [('patient_id', '=', self.id)],
            'context': {'default_patient_id': self.id},
        }

    def action_create_lab_test(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Lab Test',
            'res_model': 'medical.patient.lab.test',
            # Replace with your actual appointment model name
            'view_mode': 'form',
            'context': {
                'default_patient_id': self.id,
                # You can add more default values here if needed
            },
        }

    def _compute_invoice_count(self):
        for patient in self:
            patient.invoice_count = self.env['account.move'].search_count([('partner_id', '=', patient.patient_id.id)])

    def action_view_invoices(self):
        invoices = self.env['account.move'].search([('partner_id', '=', self.patient_id.id)])
        action = self.env.ref('account.action_move_out_invoice_type').read()[0]
        action['domain'] = [('id', 'in', invoices.ids)]
        action['context'] = {'default_partner_id': self.patient_id.id}
        return action
# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
