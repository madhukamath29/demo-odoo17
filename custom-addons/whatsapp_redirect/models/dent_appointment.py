# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Jumana Jabin MP (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api, _


class ResAppointment(models.Model):
    """Extends the medical_appointment model to add a new action for sending WhatsApp
    messages."""
    _inherit = 'medical.appointment'

    whatsapp_number = fields.Char(string="WhatsApp Number")

    def action_send_msg(self):
        """This function is called when the user clicks the
        'Send WhatsApp Message' button on an appointment's form view. It opens a
        new wizard to compose and send a WhatsApp message."""
        return {
            'type': 'ir.actions.act_window',
            'name': _('WhatsApp Message'),
            'res_model': 'whatsapp.send.message',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {'default_user_id': self.patient_id.patient_id.id,
                        'default_appointment_id': self.id},
        }


