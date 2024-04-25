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
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    comment = fields.Html(string='Notes')

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

        current_datetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # Include time information
        new_name = f'ORD{current_datetime}'

        for record in self:
            record.write({
                'name': new_name,
                'status_id': confirmed_status.id,
                'is_confirmed': True,
                'tracking_no': new_name
            })

    def action_create_custom(self):
        existing_custom = self.env['customs.customs'].search([('order_id', '=', self.id)], limit=1)
        if existing_custom:
            return {
                'name': "View/Edit Custom",
                'view_mode': 'form',
                'res_model': 'customs.customs',
                'type': 'ir.actions.act_window',
                'res_id': existing_custom.id,
                'target': 'current',
            }
        else:
            # Create a new custom record and link it to this order
            custom_values = {
                'product': self.name,  # You can adjust these fields as needed
                'order_id': self.id,
            }
            new_custom = self.env['customs.customs'].create(custom_values)
            return {
                'name': "Custom",
                'view_mode': 'form',
                'res_model': 'customs.customs',
                'type': 'ir.actions.act_window',
                'res_id': new_custom.id,
                'target': 'current',
            }


class Consignment(models.Model):
    _name = "inv.consignment"
    _description = 'Consignment Model'

    freight_order_id = fields.Many2one("inv.freightorder", string="Freight Order")
    master_bill_no = fields.Char("Master Bill No", readonly=True, default='/')
    booking_no = fields.Char("Booking No", readonly=True, default='/')
    document_ids = fields.One2many('consignment.document', 'document_id', string="Document", copy=True)
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
        ('agent', 'Agent'),
        ('customer & agent','Customer & Agent')
    ], string="Customer Y/N : ")

    customs_code = fields.Char(string="Customs Code")
    cus_code = fields.Char(string="Customer Code")
    freeze = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ])
    customer = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Customer Y/N : ")

    overseas = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Overseas Y/N : ")
    supplier_code = fields.Char(string="Supplier Code")
    local_wh = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string="Local Warehouse Y/N : ")
    ccc_code = fields.Char(string="CCA Code")
    atf_no = fields.Char(string="ATF No")
    gst_no = fields.Char(string="GST No")
    company_no = fields.Char(string="Company No")

class freightorderPackage(models.Model):
    _name = 'inv.freightorder.package'
    _description = 'Freight Order Package'

    order_id = fields.Many2one('inv.freightorder', string="Freight Order", required=True, ondelete='cascade')
    package_type_id = fields.Many2one('package.type', string="Package Type")
    unit_of_weight = fields.Float("Weight")
    weight_uom_id = fields.Many2one('uom.uom', string="Unit", domain="[('category_id.name', 'ilike', 'Weight')]")
    unit_of_volume = fields.Float("Volume")
    volume_uom_id = fields.Many2one('uom.uom', string="Unit", domain="[('category_id.name', 'ilike', 'volume')]")
    product_description = fields.Text("Product Description")
    package_count = fields.Float("Package Count")


class Customs(models.Model):
    _name = "customs.customs"  # Adjust the model name to follow the format <module_name>.<model_name>
    _description = "Customs"

    product = fields.Char(string="Product")
    hs_code = fields.Char(string="HS Code")
    export_code = fields.Char(string="Export Code")
    invoice_no = fields.Char(string="Invoice No")
    delivery_authority = fields.Char(string="Delivery Authority")
    term = fields.Char(string="Term")
    invoice_amount = fields.Float(string="Invoice Amount")
    currency_id = fields.Many2one('res.currency', string="Currency")
    exc_rate = fields.Many2one('res.currency.rate', string="Currency", domain="[('currency_id', '=', currency_id)]")
    lc_amount = fields.Float(string="LC Amount")
    gst_percentage = fields.Float(string="GST %")
    gst_value = fields.Float(string="GST Value")
    line_total = fields.Float(string="Line Total")
    currency_rate = fields.Float(string='Currency Rate')
    freight_amount = fields.Float(string='Freight Amount')
    exc_rate_1 = fields.Float(string='Exc Rate')
    lc_amount_1 = fields.Float(string='LC Amount')
    insurance_amount = fields.Float(string='Insurance Amount')
    ins_currency = fields.Char(string='Ins. Currency')
    exc_rate_2 = fields.Float(string='Exc Rate')
    lc_amount_2 = fields.Float(string='LC Amount')
    foreign_freight = fields.Float(string='Foreign Freight')
    packing_cost = fields.Float(string='Packing Cost')
    commission = fields.Float(string='Commission')
    discount = fields.Float(string='Discount')
    land_charge = fields.Float(string='Land Charge')
    processing_port = fields.Char(string='Processing Port')
    total_weight = fields.Float(string='Total Weight')
    no_of_packs = fields.Integer(string='No of Packs')
    country_of_origin = fields.Char(string='Country of origin')
    country_of_destination = fields.Char(string='Country of Destination')
    uop = fields.Char(string='UOP')
    duty = fields.Float(string='Duty')
    levy = fields.Float(string='Levy')
    total = fields.Float(string='Total')
    type = fields.Selection([
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('type3', 'Type 3'),
    ], string='Type')
    amount = fields.Float(string='Amount')

    fob_fc = fields.Float(string='FOB(FC)')
    fob_lc = fields.Float(string='FOB(LC)')
    solid_consign = fields.Selection([
        ('solid', 'Solid'),
        ('consign', 'Consign'),
    ], string='Solid/Consign')
    style = fields.Char(string='Style')
    edi_date = fields.Date(string='EDI Date')
    response = fields.Char(string='Response')
    order_id = fields.Many2one('inv.freightorder', string='Freight Order')


class Document(models.Model):
    _name = "consignment.document"
    _description = "Document"

    attachment_id = fields.Binary(string="Document")
    document_id = fields.Many2one('inv.consignment', string="Main Model")
    document_name = fields.Char(string="Document Name")
    document_url = fields.Char(string="Document URL", compute="_compute_document_url")

    @api.depends('attachment_id')
    def _compute_document_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            if record.attachment_id:
                record.document_url = base_url + '/web/content/?model=consignment.document&id=' + str(
                    record.id) + '&filename_field=document_name&field=attachment_id'
            else:
                record.document_url = False

    def open_document_preview(self):
        if self.attachment_id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.document_url,  # Use the computed document URL
                'target': 'new',
            }
        else:
            # Handle the case where there is no attachment
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': {'message': 'No document available for preview.'},
                'name': 'Document Preview',
            }
