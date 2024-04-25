import logging
import random
import string

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.safe_eval import datetime, _logger


class Port(models.Model):
    _name = "port"
    _description = "Port"

    name = fields.Char("Port Name", required=True)
    country_id = fields.Many2one("res.country", string="Country")


class PackageType(models.Model):
    _name = "package.type"
    _description = "Package Type"

    name = fields.Char("Package Type", required=True)


class ConsignmentType(models.Model):
    _name = "consignment.type"
    _description = "Consignment Type"

    name = fields.Char("Type Name", required=True)


class Mode(models.Model):
    _name = "mode"
    _description = "Mode"

    name = fields.Char("Mode Name", required=True)


class TransportType(models.Model):
    _name = "transport.type"
    _description = "Transport Type"

    name = fields.Char("Transport Type Name", required=True)
    mode_ids = fields.Many2many("mode", string="Modes")


class freightorderStatus(models.Model):
    _name = "freight.order.status"
    _description = "Freight Order Status"

    name = fields.Char("Status Name", required=True)

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        return super(freightorderStatus, self).create(values)

    def write(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        return super(freightorderStatus, self).write(values)


class chargetype(models.Model):
    _name = "charge.type"
    _description = "Charge Type"

    name = fields.Char("Charge Type", required=True)


class freightconsignmentStatus(models.Model):
    _name = "freight.consignment.status"
    _description = "Freight Consignment Status"

    name = fields.Char("Status Name", required=True)

    @api.model
    def create(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        return super(freightconsignmentStatus, self).create(values)

    def write(self, values):
        if 'name' in values:
            values['name'] = values['name'].upper()
        return super(freightconsignmentStatus, self).write(values)


class freightorder(models.Model):
    _name = "inv.freightorder"
    _description = 'Freight Order Model'
    _rec_name = 'name'

    name = fields.Char("Order id", copy=False, readonly=True, default='New')
    order_date = fields.Date("Order Date")
    ready_date = fields.Date("Ready Date")
    tracking_no = fields.Char("Tracking No")
    term = fields.Char("Term")
    shipper_id = fields.Many2one("res.partner", string="Shipper", domain="[('user_category', 'ilike', 'agent')]")
    receiver_id = fields.Many2one("res.partner", string="Receiver", domain="[('user_category', 'ilike', 'agent')]")
    bill_to_id = fields.Many2one("res.partner", string="Bill To", domain="[('user_category', 'ilike', 'customer')]")
    notify_party_id = fields.Many2one("res.partner", string="Notify Party",
                                      domain="[('user_category', 'ilike', 'customer')]")
    origin_port_id = fields.Many2one("port", string="Origin Port", )
    destination_port_id = fields.Many2one("port", string="Destination Port")
    consignment_type_id = fields.Many2one("consignment.type", string="Consignment Type")
    transport_type_id = fields.Many2one("transport.type", string="Transport Type")
    mode_id = fields.Many2one("mode", string="Mode", )
    company_id = fields.Many2one("res.company", string="Company")
    shipping_date = fields.Date("Shipping Date")
    is_confirmed = fields.Boolean("Confirmed", default=False)

    convey_name = fields.Char("Convey Name")
    lloyds_no = fields.Char("LLOYDS No")
    voyage = fields.Char("Voyage")
    flight = fields.Char("Flight")
    loading_date = fields.Date("Loading Date")
    loading_charge_type = fields.Many2one("charge.type", string="Charge Type")
    routing_charge_type = fields.Many2one("charge.type", string="Charge Type")
    departure_date = fields.Date("Departure Date")
    departure_charge_type = fields.Many2one("charge.type", string="Departure Charge Type")
    routing_country = fields.Many2one("res.country", string="Routing Country")
    routing_port = fields.Many2one("port", string="Routing Port")
    routing_date = fields.Date("Routing Date")
    delivery_charge_type = fields.Many2one("charge.type", string="Charge Type")
    delivery_date = fields.Date("Delivery Date")
    release = fields.Char("Release")
    shipper_ref = fields.Char("Shipper Ref")
    marks_and_numbers = fields.Text("Mark's and Numbers")
    goods_desc = fields.Text("Goods Desc")

    @api.model
    def _default_status_id(self):
        # Retrieve the ID of the 'New' status dynamically
        new_status = self.env['freight.order.status'].search([('name', 'ilike', 'New')], limit=1)
        return new_status.id if new_status else False

    status_id = fields.Many2one("freight.order.status", string="Status", default=_default_status_id)
    notes = fields.Text("Notes")

    origin_country_id = fields.Many2one("res.country", string="Origin Country")
    destination_country_id = fields.Many2one("res.country", string="Destination Country")
    package_ids = fields.One2many('inv.freightorder.package', 'order_id', string="Packages", copy=True)

    def action_confirm(self):
        confirmed_status = self.env['freight.order.status'].search([('name', 'ilike', 'Confirmed')], limit=1)
        if not confirmed_status:
            raise UserError("Confirmed status not found. Please make sure it's created.")

        current_date = datetime.datetime.now().strftime("%Y%m%d")
        new_name = f'ORD{current_date}'

        for record in self:
            record.write({
                'name': new_name,
                'status_id': confirmed_status.id,
                'is_confirmed': True,
                'tracking_no': new_name
            })


class Consignment(models.Model):
    _name = "inv.consignment"
    _description = 'Consignment Model'

    freight_order_id = fields.Many2one("inv.freightorder", string="Freight Order")
    master_bill_no = fields.Char("Master Bill No", readonly=True, default='/')
    booking_no = fields.Char("Booking No", readonly=True, default='/')
    term = fields.Char("Terms")
    ship_date = fields.Date("Ship Date")
    departure_date = fields.Date("Departure Date")
    arrival_date = fields.Date("Arrival Date")
    origin_port_id = fields.Many2one("port", string="Origin Port")
    origin_country_id = fields.Many2one("res.country", string="Origin Country")
    company_id = fields.Many2one("res.company", string="Company")
    destination_port_id = fields.Many2one("port", string="Destination Port")
    destination_country_id = fields.Many2one("res.country", string="Destination Country")
    sending_agent = fields.Many2one("res.partner", string="Sending Agent",
                                    domain="[('user_category', 'ilike', 'agent')]")
    receiving_agent = fields.Many2one("res.partner", string="Receiving Agent",
                                      domain="[('user_category', 'ilike', 'agent')]")
    notify_party_id = fields.Many2one("res.partner", string="Notify Party",
                                      domain="[('user_category', 'ilike', 'customer')]")
    consignment_type_id = fields.Many2one("consignment.type", string="Consignment Type")
    transport_type_id = fields.Many2one("transport.type", string="Transport Type")
    mode_id = fields.Many2one("mode", string="Mode")
    outern_no = fields.Char("Outern No")
    release_type = fields.Char("Release Type")
    carrier_name = fields.Char("Carrier Name")
    carrier_booking_ref = fields.Char("Carrier Booking Ref")
    carrier_no = fields.Char("Carrier No")
    agent_ref = fields.Many2one("res.partner", string="Agent Reference",
                                domain="[('user_category', 'ilike', 'customer')]")
    description = fields.Text("Description")
    is_confirmed = fields.Boolean("Confirmed", default=False)
    status_id = fields.Many2one("freight.consignment.status", string="Status",
                                default=lambda self: self._default_status_id())

    filtered_orders = fields.Many2many("inv.freightorder", string="Filtered Orders")

    total_package_count = fields.Float(
        string="Total Package Count",
        compute="_compute_total_package_count",
        store=True,
        help="Total package count from associated orders"
    )
    total_volume = fields.Char(
        string="Total Volume",
        compute="_compute_total_volume",
        store=True,
        help="Total volume from associated orders with unit"
    )

    total_weight = fields.Char(
        string="Total Weight",
        compute="_compute_total_weight",
        store=True,
        help="Total weight from associated orders with unit"
    )

    def print_the_action(self):
        print(self.master_bill_no);

    @api.depends('filtered_orders.package_ids.unit_of_weight', 'filtered_orders.package_ids.weight_uom_id')
    def _compute_total_weight(self):
        for consignment in self:
            total_weight = 0.0
            weight_uom = None
            for order in consignment.filtered_orders:
                for package in order.package_ids:
                    total_weight += package.unit_of_weight
                    weight_uom = package.weight_uom_id.name
            consignment.total_weight = f"{total_weight} {weight_uom}" if weight_uom else False

    @api.depends('filtered_orders.package_ids.unit_of_volume', 'filtered_orders.package_ids.volume_uom_id')
    def _compute_total_volume(self):
        for consignment in self:
            total_volume = 0.0
            volume_uom = None
            for order in consignment.filtered_orders:
                for package in order.package_ids:
                    total_volume += package.unit_of_volume
                    volume_uom = package.volume_uom_id.name
            consignment.total_volume = f"{total_volume} {volume_uom}" if volume_uom else False

    @api.depends('filtered_orders.package_ids.package_count')
    def _compute_total_package_count(self):
        for consignment in self:
            total_count = 0.0
            for order in consignment.filtered_orders:
                total_count += sum(order.package_ids.mapped('package_count'))
            consignment.total_package_count = total_count

    def generate_numbers(self):
        confirmed_status = self.env['freight.consignment.status'].search([('name', 'ilike', 'Confirmed')], limit=1)
        if not confirmed_status:
            raise UserError("Confirmed status not found. Please make sure it's created.")
        current_date = fields.Datetime.now().strftime("%Y%m%d")
        master_bill_no = current_date + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        booking_no = current_date + ''.join(random.choices(string.digits, k=6))

        self.write({
            'master_bill_no': master_bill_no,
            'booking_no': booking_no,
            'is_confirmed': True,
            'status_id': confirmed_status.id,
        })

    @api.model
    def _default_status_id(self):
        new_status = self.env['freight.consignment.status'].search([('name', 'ilike', 'New')], limit=1)
        if not new_status:
            raise UserError("New status not found. Please make sure it's created.")
        return new_status.id


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    user_category = fields.Selection([
        ('customer', 'Customer'),
        ('agent', 'Agent')
    ], string='User Category')



class freightorderPackage(models.Model):
    _name = 'inv.freightorder.package'
    _description = 'Freight Order Package'

    order_id = fields.Many2one('inv.freightorder', string="Freight Order", required=True, ondelete='cascade')
    package_type_id = fields.Many2one('package.type', string="Package Type")
    unit_of_weight = fields.Float("Unit")
    weight_uom_id = fields.Many2one('uom.uom', string="Weight", domain="[('category_id.name', 'ilike', 'Weight')]")
    unit_of_volume = fields.Float("Unit")
    volume_uom_id = fields.Many2one('uom.uom', string="Volume", domain="[('category_id.name', 'ilike', 'volume')]")
    product_description = fields.Text("Product Description")
    package_count = fields.Float("Package Count")
