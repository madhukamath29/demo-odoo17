# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class FreightOrder(models.Model):
    _name = "freight.order"

    name = fields.Char(default="New", copy=False)
    order_date = fields.Date()
    terms = fields.Char()
    shipper_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Shipper'])]")
    receiver_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Customer'])]")
    bill_to_partner_id = fields.Many2one("res.partner", string="Bill To")
    notify_party_id = fields.Many2one("res.partner", string="Notify Party")
    transport_type_id = fields.Many2one("transport.type")
    allowed_transport_mode_ids = fields.Many2many("transport.mode",
                                                  related="transport_type_id.transport_mode_ids")
    transport_mode_id = fields.Many2one("transport.mode", domain="[('id', 'in', allowed_transport_mode_ids)]")
    origin_country_id = fields.Many2one("res.country")
    origin_port_id = fields.Many2one("port.port",
                                     domain="[('country_id', '=', origin_country_id), ('transport_type_id', '=', transport_type_id)]")
    destination_country_id = fields.Many2one("res.country")
    destination_port_id = fields.Many2one("port.port",
                                          domain="[('country_id', '=', destination_country_id), ('transport_type_id', '=', transport_type_id)]")
    consignment_type = fields.Selection(
        [("import", "Import"), ("export", "Export"), ("domestic", "Domestic"), ("transhipment", "Transhipment")])
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    ready_date = fields.Date()
    shipping_date = fields.Date()
    state = fields.Selection([("planned", "Planned"), ("confirm", "Confirmed"), ("cancelled", "Cancelled")],
                             default="planned", copy=False)
    internal_note = fields.Text()
    freight_package_line_ids = fields.One2many("freight.package.line", "freight_order_id")
    in_consignment = fields.Boolean(copy=False)
    consignment_id = fields.Many2one("freight.consignment", copy=False)

    def action_open_consignment(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Consignment",
            "res_model": "freight.consignment",
            "view_mode": "form",
            'res_id': self.consignment_id.id,
        }

    @api.onchange("transport_type_id")
    def onchange_transport(self):
        self.transport_mode_id = False
        self.origin_port_id = False
        self.destination_port_id = False

    @api.onchange("origin_country_id")
    def onchange_origin_country(self):
        self.origin_port_id = False

    @api.onchange("destination_country_id")
    def onchange_destination_country(self):
        self.destination_port_id = False

    def action_confirm(self):
        self.state = "confirm"

    def action_cancel(self):
        self.state = "cancelled"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('freight.order') or _('New')
        return super().create(vals_list)


class FreightPackageLine(models.Model):
    _name = "freight.package.line"

    freight_order_id = fields.Many2one("freight.order")
    package_type = fields.Selection([("carton", "Carton"), ("container", "Container")])
    package_count = fields.Integer()
    weight = fields.Float()
    weight_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Weight')]")
    volume = fields.Float()
    volume_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Volume')]")
    description = fields.Text()
