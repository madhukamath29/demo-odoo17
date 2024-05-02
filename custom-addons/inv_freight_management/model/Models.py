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
    sub_bill_no = fields.Char("Sub Bill")
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
    master_bill_no = fields.Many2one("inv.consignment", string="Master Bill No", readonly=True)
    total_weight = fields.Char(string="Total Weight", compute='_compute_total_weight')
    total_volume = fields.Char(string="Total Volume", compute='_compute_total_volume')
    total_package_count = fields.Char(string="Total Package Count", compute='_compute_total_package_count')

    @api.depends('package_ids.unit_of_weight', 'package_ids.weight_uom_id')
    def _compute_total_weight(self):
        for order in self:
            total_weight = 0.0
            weight_uom = None
            for package in order.package_ids:
                total_weight += package.unit_of_weight
                weight_uom = package.weight_uom_id.name
            order.total_weight = f"{total_weight} {weight_uom}" if weight_uom else False

    @api.depends('package_ids.unit_of_volume', 'package_ids.volume_uom_id')
    def _compute_total_volume(self):
        for order in self:
            total_volume = 0.0
            volume_uom = None
            for package in order.package_ids:
                total_volume += package.unit_of_volume
                volume_uom = package.volume_uom_id.name
            order.total_volume = f"{total_volume} {volume_uom}" if volume_uom else False

    @api.depends('package_ids.package_count', 'package_ids.package_type_id')
    def _compute_total_package_count(self):
        for order in self:
            package_counts = {}
            for package in order.package_ids:
                package_type = package.package_type_id.name
                if package_type not in package_counts:
                    package_counts[package_type] = 0
                package_counts[package_type] += package.package_count

            total_package_count_str = ", ".join(
                [f"{count} {package_type}" for package_type, count in package_counts.items()])
            order.total_package_count = total_package_count_str

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
    product_ids = fields.One2many('freight.product', 'order_id', string="Products", copy=True)
    total_product_quantity = fields.Char(string="Total Product Quantity", compute='_compute_total_product_quantity')
    total_product_weight = fields.Char(string="Total Product Weight", compute='_compute_total_product_weight')
    total_product_volume = fields.Char(string="Total Product Volume", compute='_compute_total_product_volume')

    @api.depends('product_ids.quantity', 'product_ids.quantity_unit_id')
    def _compute_total_product_quantity(self):
        for order in self:
            total_quantity = sum(order.product_ids.mapped('quantity'))
            unit = order.product_ids and order.product_ids[0].quantity_unit_id.name or ''
            order.total_product_quantity = f"{total_quantity} {unit}"

    @api.depends('product_ids.weight', 'product_ids.weight_unit_id')
    def _compute_total_product_weight(self):
        for order in self:
            total_weight = sum(order.product_ids.mapped('weight'))
            unit = order.product_ids and order.product_ids[0].weight_unit_id.name or ''
            order.total_product_weight = f"{total_weight} {unit}"

    @api.depends('product_ids.volume', 'product_ids.volume_unit_id')
    def _compute_total_product_volume(self):
        for order in self:
            total_volume = sum(order.product_ids.mapped('volume'))
            unit = order.product_ids and order.product_ids[0].volume_unit_id.name or ''
            order.total_product_volume = f"{total_volume} {unit}"

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
                'tracking_no': new_name,
                'order_date': fields.Date.today().strftime("%Y-%m-%d")
            })

    def update_product_details(self):
        # Fetch all product names associated with this order
        product_names = ', '.join(self.product_ids.mapped('name'))

        # Update the products field in the customs model
        for customs_record in self.env['customs.customs'].search([('order_id', '=', self.id)]):
            customs_record.write(
                {'product': product_names, 'total_weight': self.total_product_weight,
                 'no_of_packs': self.total_product_quantity,
                 'country_of_origin': self.origin_country_id.id,
                 'country_of_destination': self.destination_country_id.id,
                 'processing_port': self.origin_port_id.id,
                 'invoice_no': self.product_ids.invoice_no,
                 'invoice_amount': self.product_ids.invoice_total,
                 'exc_rate': self.product_ids.exchange_rate.id,
                 'currency_id': self.product_ids.currency_id.id,

                 })

    def action_create_custom(self):
        # Check if there's an existing customs entry for this order
        existing_custom = self.env['customs.customs'].search([('order_id', '=', self.id)], limit=1)
        if existing_custom:
            # Update the product details in existing customs entry
            self.update_product_details()
            return {
                'name': "View/Edit Custom",
                'view_mode': 'form',
                'res_model': 'customs.customs',
                'type': 'ir.actions.act_window',
                'res_id': existing_custom.id,
                'target': 'current',
            }
        else:
            # Create a new customs entry
            new_custom = self.env['customs.customs'].create({'order_id': self.id})

            # Update the product details in the new customs entry
            self.update_product_details()

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
    name = fields.Char("Master Bill No", readonly=True, default='/')
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

    consignment_order_ids = fields.One2many("inv.freightorder", "name", string="Consignment Orders")

    @api.onchange('filtered_orders')
    def _onchange_filtered_orders(self):
        """
        Update master_bill_no field of related orders when filtered_orders change.
        """
        print("_onchange_filtered_orders")

        # Save the consignment record to ensure its ID is available
        self.ensure_one()  # Ensure only one record is being processed
        self.write({})  # Save the record (no actual changes)

        # Assign consignment_id to master_bill_no field of related orders
        for order in self.filtered_orders:
            print("Assigning consignment to order:", order)
            print("self.id", self.id)
            order.master_bill_no = self.name  # Assign consignment ID to master_bill_no field of the order

            # Explicitly save the record to persist changes
            order.write({'master_bill_no': self.name})

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
        name = current_date + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        booking_no = current_date + ''.join(random.choices(string.digits, k=6))

        self.write({
            'name': name,
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

    user_category = fields.Many2many('user.role', string="Role")

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
    package_count = fields.Integer("Package Count")
    container_no = fields.Char(string="Container No")
    container_type = fields.Char(string="Container Type")
    container_weight = fields.Float(string="Container Weight")
    container_weight_unit = fields.Many2one('uom.uom', string="Unit",
                                            domain="[('category_id.name', 'ilike', 'Weight')]")
    gross_weight = fields.Float(string="Gross Weight")
    gross_weight_unit = fields.Many2one('uom.uom', string="Unit", domain="[('category_id.name', 'ilike', 'Weight')]")
    temperature = fields.Float(string="Temperature")
    airflow = fields.Integer(string="Airflow")
    seal_no = fields.Char(string="Seal No")
    marks = fields.Char(string="Marks")
    packing_material = fields.Text(string="Packing Material")


class Customs(models.Model):
    _name = "customs.customs"  # Adjust the model name to follow the format <module_name>.<model_name>
    _description = "Customs"

    order_id = fields.Many2one('inv.freightorder', string='Freight Order')
    product = fields.Text(string="Product")
    hs_code = fields.Char(string="HS Code")
    export_code = fields.Char(string="Export Code")
    invoice_no = fields.Char(string="Invoice No")
    delivery_authority = fields.Char(string="Delivery Authority")
    term = fields.Char(string="Term")
    invoice_amount = fields.Float(string="Invoice Amount")
    currency_id = fields.Many2one('res.currency', string="Currency")
    exc_rate = fields.Many2one('res.currency.rate', string="Exc Rate", domain="[('currency_id', '=', currency_id)]")
    lc_amount = fields.Float(string="LC Amount", compute='_compute_lc_amount', store=True, readonly=True)
    gst_percentage = fields.Float(string="GST %")
    gst_value = fields.Float(string="GST Value", compute='_compute_gst_value', store=True, readonly=True)
    line_total = fields.Float(string="Line Total", compute='_compute_line_total', store=True, readonly=True)
    currency_rate = fields.Selection([
        ('floating', 'Floating'),
        ('forward_cover', 'Forward Cover'),
        ('nz_dollar', 'NZ Dollar')],
        string="Currency Rate")
    freight_amount = fields.Float(string='Freight Amount')
    freight_currency = fields.Many2one('res.currency', string="Freight Currency")
    exc_rate_1 = fields.Many2one('res.currency.rate', string="Exc Rate",
                                 domain="[('currency_id', '=', freight_currency)]")
    lc_amount_1 = fields.Float(string="LC Amount", compute='_compute_lc_amount_1', store=True, readonly=True)
    insurance_amount = fields.Float(string='Insurance Amount')
    ins_currency = fields.Many2one('res.currency', string="Insurance Currency")
    exc_rate_2 = fields.Many2one('res.currency.rate', string="Exc Rate", domain="[('currency_id', '=',ins_currency )]")
    lc_amount_2 = fields.Float(string="LC Amount", compute='_compute_lc_amount_2', store=True, readonly=True)
    foreign_freight = fields.Char(string='Foreign Freight')
    packing_cost = fields.Float(string='Packing Cost')
    commission = fields.Float(string='Commission')
    discount = fields.Float(string='Discount')
    land_charge = fields.Char(string='Land Charge')
    processing_port = fields.Many2one("port", string="Origin Port", )
    total_weight = fields.Char(string='Total Weight')
    no_of_packs = fields.Char(string='No of Packs')
    country_of_origin = fields.Many2one("res.country", string="Origin Country")
    country_of_destination = fields.Many2one("res.country", string="Country of Destination")
    uop = fields.Char(string='UOP')
    duty = fields.Float(string='Duty')
    levy = fields.Float(string='Levy')
    total = fields.Float(string='Total')
    type = fields.Char(string='Type')
    amount = fields.Float(string='Amount')
    currency = fields.Many2one('res.currency', string="Currency")
    exc_rate_4 = fields.Float(string='Exc Rate')
    fob_fc = fields.Float(string='FOB(FC)')
    fob_lc = fields.Float(string='FOB(LC)')
    solid_consign = fields.Selection([
        ('solid', 'Solid'),
        ('consign', 'Consign'),
    ], string='Solid/Consign')
    style = fields.Selection([('normal', 'Normal'),
                              ('drawback', 'Drawback'),
                              ('completion', 'Completion'), ], string='Style')
    edi_date = fields.Date(string='EDI Date', readonly=True)
    response = fields.Char(string='Response', readonly=True)

    @api.depends('invoice_amount', 'exc_rate.rate')
    def _compute_lc_amount(self):
        for record in self:
            if record.exc_rate and record.exc_rate.rate:
                record.lc_amount = record.invoice_amount / record.exc_rate.rate
            else:
                record.lc_amount = 0.0

    @api.depends('invoice_amount', 'exc_rate.rate')
    def _compute_lc_amount_2(self):
        for record in self:
            if record.exc_rate_2 and record.exc_rate_2.rate:
                record.lc_amount_2 = record.insurance_amount / record.exc_rate_2.rate
            else:
                record.lc_amount_2 = 0.0

    @api.depends('invoice_amount', 'exc_rate.rate')
    def _compute_lc_amount_1(self):
        for record in self:
            if record.exc_rate_1 and record.exc_rate_1.rate:
                record.lc_amount_1 = record.freight_amount / record.exc_rate_1.rate
            else:
                record.lc_amount_1 = 0.0

    @api.depends('invoice_amount', 'gst_percentage')
    def _compute_gst_value(self):
        for record in self:
            record.gst_value = (record.invoice_amount * record.gst_percentage) / 100

    @api.depends('lc_amount', 'gst_value')
    def _compute_line_total(self):
        for record in self:
            record.line_total = record.lc_amount + record.gst_value


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


class Role(models.Model):
    _name = 'user.role'
    _description = 'User Role'

    name = fields.Char(string="Role Name")


class FreightProduct(models.Model):
    _name = 'freight.product'
    _description = 'Freight Product'

    order_id = fields.Many2one('inv.freightorder', string="Freight Order", required=True, ondelete='cascade')
    name = fields.Char(string="Product Name", required=True)
    description = fields.Text(string="Description")
    brand = fields.Char(string="Brand")
    supplier = fields.Many2one("res.partner", string="Shipper", domain="[('user_category', 'ilike', 'supplier')]")
    invoice_no = fields.Char(string="Invoice No")
    invoice_total = fields.Float(string="Invoice Total")
    currency_id = fields.Many2one('res.currency', string="Currency")
    exchange_rate = fields.Many2one('res.currency.rate', string="Exc Rate",
                                    domain="[('currency_id', '=', currency_id)]")
    quantity = fields.Integer(string="Quantity")
    quantity_unit_id = fields.Many2one('package.type', string="Package Type")
    weight = fields.Float(string="Weight")
    weight_unit_id = fields.Many2one('uom.uom', string="Unit", domain="[('category_id.name', 'ilike', 'Weight')]")
    volume = fields.Float(string="Volume")
    volume_unit_id = fields.Many2one('uom.uom', string="Unit", domain="[('category_id.name', 'ilike', 'Volume')]")
    country_of_origin = fields.Char(string="Country of Origin")
    country_of_import = fields.Char(string="Country of Import")
    country_of_export = fields.Char(string="Country of Export")
    packing_material = fields.Text(string="Packing Material")

    @api.depends('weight', 'weight_unit_id')
    def _compute_display_weight(self):
        for record in self:
            if record.weight and record.weight_unit_id:
                record.display_weight = f"{record.weight} {record.weight_unit_id.name}"
            else:
                record.display_weight = False

    display_weight = fields.Char(string="Weight (with Unit)", compute="_compute_display_weight", store=True)

    @api.depends('quantity', 'quantity_unit_id')
    def _compute_display_quantity(self):
        for record in self:
            if record.quantity and record.quantity_unit_id:
                record.display_quantity = f"{record.quantity} {record.quantity_unit_id.name}"
            else:
                record.display_quantity = False

    display_quantity = fields.Char(string="Quantity (with Unit)", compute="_compute_display_quantity", store=True)

    @api.depends('volume', 'volume_unit_id')
    def _compute_display_volume(self):
        for record in self:
            if record.volume and record.volume_unit_id:
                record.display_volume = f"{record.volume} {record.volume_unit_id.name}"
            else:
                record.display_volume = False

    display_volume = fields.Char(string="Volume (with Unit)", compute="_compute_display_volume", store=True)
