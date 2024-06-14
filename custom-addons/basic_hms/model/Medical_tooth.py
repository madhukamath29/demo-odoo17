from odoo import api, fields, models


class MedicalTooth(models.Model):
    _name = 'medical.tooth'
    _description = 'Medical Tooth'

    image_field = fields.Binary(string="Upload X-ray Image")

    # upper_left = fields.Selection(
    #     [('s', 'Upper Right Quadrant'), ('m', 'Upper Left Quadrant'),
    #      ('w', 'Lower Left Quadrant'), ('d', 'Lower Right Quadrant')],
    #     string='Tooth Position', required=True)
    upper_right = fields.Selection(
        [('s', 'Upper Right Quadrant'), ('m', 'Upper Left Quadrant'),
         ('w', 'Lower Left Quadrant'), ('d', 'Lower Right Quadrant')],
        string='Tooth Position', required=True)
    tooth_type = fields.Selection(
        selection='_get_tooth_type_selection', string='Tooth Type')

    problem_type = fields.Selection(
        selection='_get_problem_type_selection', string='Problem Type')
    patient_id = fields.Many2one('medical.patient', string="Patient")
    solution = fields.Text(string='Solution')

    @api.model
    @api.model
    def _get_tooth_type_selection(self):
        return [
            ('1', '1: Wisdom Tooth (3rd Molar)'),
            ('2', '2: Molar (2nd Molar)'),
            ('3', '3: Molar (1st Molar)'),
            ('4', '4: Bicuspid (2nd)'),
            ('5', '5: Bicuspid (1st)'),
            ('6', '6: Canine (Cuspid/Eye Tooth)'),
            ('7', '7: Incisor (Lateral)'),
            ('8', '8: Incisor (Central)'),
            ('9', '9: Incisor (Central)'),
            ('10', '10: Incisor (Lateral)'),
            ('11', '11: Canine (Cuspid/Eye Tooth)'),
            ('12', '12: Bicuspid (1st)'),
            ('13', '13: Bicuspid (2nd)'),
            ('14', '14: Molar (1st Molar)'),
            ('15', '15: Molar (2nd Molar)'),
            ('16', '16: Wisdom Tooth (3rd Molar)'),
            ('17', '17: Wisdom Tooth (3rd Molar)'),
            ('18', '18: Molar (2nd Molar)'),
            ('19', '19: Molar (1st Molar)'),
            ('20', '20: Bicuspid (2nd)'),
            ('21', '21: Bicuspid (1st)'),
            ('22', '22: Canine'),
            ('23', '23: Incisor (Lateral)'),
            ('24', '24: Incisor (Central)'),
            ('25', '25: Incisor (Central)'),
            ('26', '26: Incisor (Lateral)'),
            ('27', '27: Canine (Cuspid/Eye Tooth)'),
            ('28', '28: Bicuspid (1st)'),
            ('29', '29: Bicuspid (2nd)'),
            ('30', '30: Molar (1st Molar)'),
            ('31', '31: Molar (2nd Molar)'),
            ('32', '32: Wisdom Tooth (3rd Molar)')
        ]

    @api.model
    def _get_problem_type_selection(self):
        return [
            ('decay', 'Tooth Decay (Cavities)'),
            ('gum', 'Gum Disease (Periodontal Disease)'),
            ('sensitivity', 'Tooth Sensitivity'),
            ('cracked', 'Cracked or Broken Teeth'),
            ('erosion', 'Tooth Erosion'),
            ('abscess', 'Tooth Abscess'),
            ('discoloration', 'Tooth Discoloration'),
            ('impacted', 'Impacted Teeth'),
            ('ache', 'Toothache'),
            ('misaligned', 'Misaligned Teeth (Malocclusion)'),
            ('wear', 'Tooth Wear (Attrition)'),
            ('root_canal', 'Root Canal Infection'),
            ('dry_socket', 'Dry Socket (Alveolar Osteitis)'),
            ('fluorosis', 'Dental Fluorosis'),
            ('hyperdontia', 'Hyperdontia')
        ]

    @api.onchange('upper_right')
    def _onchange_upper_right(self):
        self.tooth_type = False  # Reset the tooth type when quadrant changes

    @api.onchange('tooth_type')
    def _onchange_tooth_type(self):
        self.problem_type = False  # Reset the problem type when tooth type changes


    def action_generate_tooth_report(self):
        # Assuming 'self' contains the current record (medical tooth details)
        # Fetch necessary data, context, and prepare for report generation
        data = {}  # Include any additional data needed for the report template

        # Return the action to render the report using the specified template
        return self.env.ref('basic_hms.report_print_patient_card').report_action(self)
