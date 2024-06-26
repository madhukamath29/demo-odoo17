import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class MedicalAppointmentsInvoiceWizard(models.TransientModel):
    _name = "medical.appointments.invoice.wizard"
    _description = 'Medical Appointments Invoice Wizard'

    def create_invoice(self):
        active_ids = self._context.get('active_ids', [])
        if not active_ids:
            raise UserError(_('No active appointments selected.'))

        lab_req_obj = self.env['medical.appointment']
        account_invoice_obj = self.env['account.move']
        ir_property_obj = self.env['ir.property']
        list_of_ids = []

        for active_id in active_ids:
            lab_req = lab_req_obj.browse(active_id)
            _logger.info('Processing appointment: %s', lab_req.name)

            if lab_req.validity_status == 'invoice':
                continue

            if lab_req.is_invoiced:
                raise UserError(_('Appointment %s is already invoiced.') % lab_req.name)

            if not lab_req.no_invoice:
                sale_journals = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
                if not sale_journals:
                    raise UserError(_('No sale journals found.'))

                invoice_vals = {
                    'name': self.env['ir.sequence'].next_by_code('medical_app_inv_seq'),
                    'invoice_origin': lab_req.name or '',
                    'move_type': 'out_invoice',
                    'ref': False,
                    'partner_id': lab_req.patient_id.patient_id.id,
                    'partner_shipping_id': lab_req.patient_id.patient_id.id,
                    'currency_id': lab_req.patient_id.patient_id.currency_id.id,
                    'invoice_payment_term_id': False,
                    'fiscal_position_id': lab_req.patient_id.patient_id.property_account_position_id.id,
                    'team_id': False,
                    'invoice_date': date.today(),
                    'journal_id': sale_journals.id,
                }
                invoice = account_invoice_obj.create(invoice_vals)
                invoice_line_account_id = lab_req.consultations_id.property_account_income_id.id or lab_req.consultations_id.categ_id.property_account_income_categ_id.id

                if not invoice_line_account_id:
                    _logger.info('Fetching income account for category: %s', lab_req.consultations_id.categ_id.name)
                    inc_acc = ir_property_obj.get_multi(['property_account_income_categ_id'], lab_req.consultations_id.categ_id)
                    if inc_acc.get('property_account_income_categ_id'):
                        invoice_line_account_id = inc_acc['property_account_income_categ_id'].id

                    if not invoice_line_account_id:
                        raise UserError(
                            _('No income account defined for product: "%s".') % lab_req.consultations_id.name)

                taxes = lab_req.consultations_id.taxes_id.filtered(
                    lambda
                        r: not lab_req.consultations_id.company_id or r.company_id == lab_req.consultations_id.company_id
                )

                invoice_line_vals = {
                    'name': lab_req.consultations_id.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit': lab_req.consultations_id.lst_price,
                    'product_uom_id': lab_req.consultations_id.uom_id.id,
                    'quantity': 1,
                    'product_id': lab_req.consultations_id.id,
                    'tax_ids': [(6, 0, taxes.ids)],
                }

                invoice.write({'invoice_line_ids': [(0, 0, invoice_line_vals)]})
                list_of_ids.append(invoice.id)
                lab_req.write({'is_invoiced': True, 'validity_status': 'invoice'})

        if list_of_ids:
            action = self.env.ref('account.action_move_out_invoice_type')
            result = {
                'name': action.name,
                'help': action.help,
                'type': action.type,
                'views': [[self.env.ref('account.view_invoice_tree').id, 'tree'], [self.env.ref('account.view_move_form').id, 'form']],
                'target': action.target,
                'context': action.context,
                'res_model': action.res_model,
                'domain': [('id', 'in', list_of_ids)]
            }
            return result
        else:
            raise UserError(_('The selected appointments are invoice exempt.'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
