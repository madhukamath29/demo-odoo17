# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OrderSelectionWizard(models.TransientModel):
    _name = "order.selection.wizard"

    order_wizard_line_ids = fields.One2many("order.line.wizard", "wizard_id")
    consignment_id = fields.Many2one("freight.consignment")

    def action_add_selected_orders(self):
        selected_order_lines = self.order_wizard_line_ids.filtered(lambda line: line.selected)
        if selected_order_lines:
            order_ids = selected_order_lines.mapped("order_id")
            consignment_orders = []

            for order_id in order_ids:
                package_lines = []
                if order_id.freight_package_line_ids:
                    for freight_package_line_id in order_id.freight_package_line_ids:
                        package_lines.append((0, 0, {
                            "package_type": freight_package_line_id.package_type,
                            "package_count": freight_package_line_id.package_count,
                            "weight": freight_package_line_id.weight,
                            "weight_uom_id": freight_package_line_id.weight_uom_id.id,
                            "volume": freight_package_line_id.volume,
                            "volume_uom_id": freight_package_line_id.volume_uom_id.id,
                            "description": freight_package_line_id.description,
                        }))
                consignment_orders.append((0, 0, {
                    "master_bill_no": self.consignment_id.master_bill_no,
                    "shipper_id": order_id.shipper_id.id,
                    "receiver_id": order_id.receiver_id.id,
                    "bill_to_partner_id": order_id.bill_to_partner_id.id,
                    "notify_party_id": order_id.notify_party_id.id,
                    "origin_country_id": self.consignment_id.origin_country_id.id,
                    "origin_port_id": self.consignment_id.origin_port_id.id,
                    "destination_country_id": self.consignment_id.destination_country_id.id,
                    "destination_port_id": self.consignment_id.destination_port_id.id,
                    "transport_type_id": self.consignment_id.transport_type_id.id,
                    "transport_mode_id": self.consignment_id.transport_mode_id.id,
                    "consignment_type": self.consignment_id.consignment_type,
                    "company_id": self.consignment_id.company_id.id,
                    "freight_order_id": order_id.id,
                    "order_date": order_id.order_date,
                    "order_package_line_ids": package_lines
                }))
                order_id.in_consignment = True
                order_id.consignment_id = self.consignment_id.id
            if consignment_orders:
                self.consignment_id.consignment_order_ids = consignment_orders
        else:
            raise ValidationError("Select orders to add in consignment!")


class OrderLineWizard(models.TransientModel):
    _name = "order.line.wizard"

    selected = fields.Boolean()
    order_id = fields.Many2one("freight.order")
    order_date = fields.Date(related="order_id.order_date")
    shipper_id = fields.Many2one(related="order_id.shipper_id")
    receiver_id = fields.Many2one(related="order_id.receiver_id")
    origin_country_id = fields.Many2one(related="order_id.origin_country_id")
    destination_country_id = fields.Many2one(related="order_id.destination_country_id")
    transport_mode_id = fields.Many2one(related="order_id.transport_mode_id")
    wizard_id = fields.Many2one("order.selection.wizard")
