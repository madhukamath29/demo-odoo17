# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime


class medical_appointments_invoice_wizard(models.TransientModel):
    _name = "medical.appointments.invoice.wizard"
    _description = 'medical appointments invoice wizard'

    def create_invoice(self):
        active_ids = self._context.get('active_ids', [])
        list_of_ids = []
        lab_req_obj = self.env['medical.appointment']
        account_invoice_obj = self.env['account.move']
        ir_property_obj = self.env['ir.property']
        for active_id in active_ids:
            lab_req = lab_req_obj.browse(active_id)
            lab_req.validity_status = 'invoice'
            if lab_req.is_invoiced:
                raise UserError(_('Already Invoiced.'))

            if lab_req.no_invoice:
                raise UserError(_('The Appointment is invoice exempt.'))
                sale_journals = self.env['account.journal'].search([('type', '=', 'sale')])
                invoice_vals = {
                    'name': self.env['ir.sequence'].next_by_code('medical_app_inv_seq'),
                    'invoice_origin': lab_req.name or '',
                    'move_type': 'out_invoice',
                    'partner_id': lab_req.patient_id.patient_id.id or False,
                    'partner_shipping_id': lab_req.patient_id.patient_id.id,
                    'currency_id': lab_req.patient_id.patient_id.currency_id.id,
                    'fiscal_position_id': lab_req.patient_id.patient_id.property_account_position_id.id,
                    'invoice_date': date.today(),
                    'journal_id': sale_journals.id,
                }
                res = account_invoice_obj.create(invoice_vals)
            # Initialize invoice_line_account_id to None
            invoice_line_account_id = None
            if lab_req.consultations_id:
                invoice_line_account_id = lab_req.consultations_id.property_account_income_id.id or \
                                          lab_req.consultations_id.categ_id.property_account_income_categ_id.id or \
                                          None
                if not invoice_line_account_id:
                    inc_acc = ir_property_obj.get_by_key('property_account_income_categ_id')
                if inc_acc:
                    invoice_line_account_id = int(inc_acc.value_reference)
            if not invoice_line_account_id:
                raise UserError(
                    _('There is no income account defined for this product: "%s". '
                      'You may have to install a chart of account from the Accounting app, settings menu.') %
                    (lab_req.consultations_id.name,))

        tax_ids = lab_req.consultations_id.taxes_id.filtered(lambda r: not lab_req.consultations_id.company_id or
                                                                       r.company_id == lab_req.consultations_id.company_id).ids
        invoice_line_vals = {
            'name': lab_req.consultations_id.name or '',
            'account_id': invoice_line_account_id,
            'price_unit': lab_req.consultations_id.lst_price,
            'product_uom_id': lab_req.consultations_id.uom_id.id,
            'quantity': 1,
            'product_id': lab_req.consultations_id.id,
            'tax_ids': [(6, 0, tax_ids)],
        }

        res.write({'invoice_line_ids': [(0, 0, invoice_line_vals)]})

        list_of_ids.append(res.id)

        lab_req.write({'is_invoiced': True})

        action = self.env.ref('account.action_move_out_invoice_type')
        list_view_id = self.env.ref('account.view_invoice_tree').id
        form_view_id = self.env.ref('account.view_move_form').id
        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [(list_view_id, 'tree'), (form_view_id, 'form')],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,

            'domain': [('id', 'in', list_of_ids)],
        }
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
