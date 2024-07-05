# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerRole(models.Model):
    _name = "res.partner.role"

    name = fields.Char()


class TransportMode(models.Model):
    _name = "transport.mode"

    name = fields.Char()


class TransportType(models.Model):
    _name = "transport.type"

    name = fields.Char()
    transport_mode_ids = fields.Many2many("transport.mode")


class Port(models.Model):
    _name = "port.port"

    name = fields.Char()
    country_id = fields.Many2one("res.country")
    transport_type_id = fields.Many2one("transport.type")


class DocumentType(models.Model):
    _name = "freight.document.type"

    name = fields.Char()


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_customer = fields.Selection([("no", "No"), ("yes", "Yes")], default="no")
    customs_code = fields.Char()
    is_overseas = fields.Selection([("no", "No"), ("yes", "Yes")], default="no")
    supplier_code = fields.Char()
    has_local_warehouse = fields.Selection([("no", "No"), ("yes", "Yes")], default="no")
    cca_code = fields.Char("CCA Code")
    atf_number = fields.Char()
    company_number = fields.Char()
    partner_role_ids = fields.Many2many("res.partner.role")
    ref_unique_code = fields.Char("Ref. Unique Code")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['ref_unique_code'] = self.env['ir.sequence'].next_by_code('res.partner.code')
        result = super(ResPartner, self).create(vals_list)
        return result


class CustomerCodeSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def generate_code(self):
        res = self.env['res.partner'].sudo().search([('ref_unique_code', '=', False)])

        for rec in res:
            if not rec.ref_unique_code:
                sequence_obj = self.env['ir.sequence']
                code = sequence_obj.next_by_code('res.partner.code')
                rec.write({'ref_unique_code': code})
        return True
