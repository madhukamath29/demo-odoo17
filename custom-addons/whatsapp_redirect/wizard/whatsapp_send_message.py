# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author:Jumana Jabin MP (odoo@cybrosys.com)
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
from odoo import fields, models, api, _


class WhatsappSendMessage(models.TransientModel):
    """This model is used for sending WhatsApp messages through Odoo."""
    _name = 'whatsapp.send.message'
    _description = "Whatsapp Wizard"

    user_id = fields.Many2one('res.partner', string="Recipient")
    mobile = fields.Char(related='user_id.mobile', required=True)
    message = fields.Text(string="Message", compute='_compute_message', store=True)
    appointment_id = fields.Many2one('medical.appointment', string="Appointment")
    res_company = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)

    @api.depends('user_id.name', 'appointment_id.doctor_id')
    def _compute_message(self):
        for record in self:
            record.message = ("Dear %s,\n\n"
                              "This is %s. Your appointment with Dr.%s  is scheduled for %s.\n\n"
                              "Please reply 'YES' to confirm or call us at %s to reschedule.\n\n"
                              "Thank you.") % (
                             record.user_id.name or '', record.res_company.name or '', record.appointment_id.doctor_id.partner_id.name or '',
                             record.appointment_id.appointment_date or '', record.res_company.phone or '')

    def action_send_message(self):
        """This method is called to send the WhatsApp message using the provided details."""
        if self.message and self.mobile:
            message_string = '+'.join(self.message.split())
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone=" + self.user_id.mobile + "&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }