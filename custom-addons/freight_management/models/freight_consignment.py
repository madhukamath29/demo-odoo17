# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class FreightConsignment(models.Model):
    _name = "freight.consignment"

    name = fields.Char(default="New")
    master_bill_no = fields.Char(required=True)
    booking_no = fields.Char(required=True)
    terms = fields.Char(required=True)
    sending_agent_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Agent'])]",
                                       required=True)
    receiving_agent_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Agent'])]",
                                         required=True)
    notify_party_id = fields.Many2one("res.partner", string="Notify Party", required=True)
    origin_country_id = fields.Many2one("res.country", required=True)
    origin_port_id = fields.Many2one("port.port", required=True,
                                     domain="[('country_id', '=', origin_country_id), ('transport_type_id', '=', transport_type_id)]")
    destination_country_id = fields.Many2one("res.country", required=True)
    destination_port_id = fields.Many2one("port.port", required=True,
                                          domain="[('country_id', '=', destination_country_id), ('transport_type_id', '=', transport_type_id)]")
    transport_type_id = fields.Many2one("transport.type", required=True)
    allowed_transport_mode_ids = fields.Many2many("transport.mode", related="transport_type_id.transport_mode_ids",
                                                  )
    transport_mode_id = fields.Many2one("transport.mode", domain="[('id', 'in', allowed_transport_mode_ids)]",
                                        required=True)
    consignment_type = fields.Selection(
        [("import", "Import"), ("export", "Export"), ("domestic", "Domestic"), ("transhipment", "Transhipment")],
        required=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    shipping_date = fields.Date(required=True)
    arrival_date = fields.Date()
    departure_date = fields.Date(required=True)
    outern_no = fields.Char()
    release_type = fields.Char()
    carrier_name = fields.Char()
    carrier_booking_ref = fields.Char()
    carrier_no = fields.Char()
    agent_ref = fields.Char()
    description = fields.Text(required=True)
    consignment_order_ids = fields.One2many("freight.consignment.order", "consignment_id")
    consignment_document_line_ids = fields.One2many("consignment.order.document.line", "consignment_id")
    consignment_customs_line_ids = fields.One2many("consignment.customs.line", "consignment_id")

    def action_open_consignment_orders(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Consignment Orders",
            "res_model": "freight.consignment.order",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.consignment_order_ids.ids)],
            "context": {"default_consignment_id": self.id, }
        }

    def action_open_consignment_customs(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Consignment Customs",
            "res_model": "consignment.customs.line",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.consignment_customs_line_ids.ids)],
            "context": {"default_consignment_id": self.id}

        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('freight.consignment.code')
        result = super(FreightConsignment, self).create(vals_list)
        return result

    @api.onchange("master_bill_no", "origin_country_id", "origin_port_id", "destination_country_id",
                  "destination_port_id", "transport_type_id", "transport_mode_id", "consignment_type", "company_id")
    def onchange_dependency_fields(self):
        if self.consignment_order_ids:
            raise ValidationError("After adding the orders you are not allowed to change this field!"
                                  "\nOtherwise delete the order to update the field value.")

    def action_pull_orders(self):
        order_ids = self.env["freight.order"].search(
            [("state", "=", "confirm"), ("in_consignment", "=", False),
             ("origin_country_id", "=", self.origin_country_id.id), ("origin_port_id", "=", self.origin_port_id.id),
             ("destination_country_id", "=", self.destination_country_id.id),
             ("destination_port_id", "=", self.destination_port_id.id),
             ("transport_type_id", "=", self.transport_type_id.id),
             ("transport_mode_id", "=", self.transport_mode_id.id)])
        print("order_ids", order_ids)
        order_wizard_line_ids = []
        for order_id in order_ids:
            order_wizard_line_ids.append((0, 0, {
                "order_id": order_id.id
            }))
        return {
            "type": "ir.actions.act_window",
            "name": "Select Consignment Orders",
            "res_model": "order.selection.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_order_wizard_line_ids": order_wizard_line_ids, "default_consignment_id": self.id}
        }


class FreightConsignmentOrder(models.Model):
    _name = "freight.consignment.order"
    _rec_name = "sub_bill_no"

    # name = fields.Char()
    order_date = fields.Date()
    consignment_id = fields.Many2one("freight.consignment", ondelete='cascade')
    master_bill_no = fields.Char(related="consignment_id.master_bill_no", store=True)
    sub_bill_no = fields.Char()
    bill_seq = fields.Integer()
    shipper_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Shipper'])]", required=True)
    receiver_id = fields.Many2one("res.partner", domain="[('partner_role_ids.name', 'in', ['Customer'])]",
                                  required=True)
    bill_to_partner_id = fields.Many2one("res.partner", string="Bill To", required=True)
    notify_party_id = fields.Many2one("res.partner", string="Notify Party", required=True)
    origin_country_id = fields.Many2one("res.country", related="consignment_id.origin_country_id",
                                        store=True)
    origin_port_id = fields.Many2one("port.port", related="consignment_id.origin_port_id",
                                     store=True)
    loading_date = fields.Date()
    loading_charge_type = fields.Selection(
        [("not_applicable", "Not Applicable"), ("prepaid", "Prepaid"), ("collect", "Collect")])
    departure_date = fields.Date()
    departure_charge_type = fields.Selection(
        [("not_applicable", "Not Applicable"), ("prepaid", "Prepaid"), ("collect", "Collect")])
    routing_country_id = fields.Many2one("res.country")
    routing_port_id = fields.Many2one("port.port",
                                      domain="[('country_id', '=', routing_country_id), ('transport_type_id', '=', transport_type_id)]")
    routing_date = fields.Date()
    routing_charge_type = fields.Selection(
        [("not_applicable", "Not Applicable"), ("prepaid", "Prepaid"), ("collect", "Collect")])
    destination_country_id = fields.Many2one("res.country",
                                             related="consignment_id.destination_country_id", store=True)
    destination_port_id = fields.Many2one("port.port", store=True,
                                          related="consignment_id.destination_port_id")
    delivery_date = fields.Date()
    delivery_charge_type = fields.Selection(
        [("not_applicable", "Not Applicable"), ("prepaid", "Prepaid"), ("collect", "Collect")])
    transport_type_id = fields.Many2one("transport.type", store=True,
                                        related="consignment_id.transport_type_id")
    transport_mode_id = fields.Many2one("transport.mode", store=True, related="consignment_id.transport_mode_id", )
    consignment_type = fields.Selection(
        [("import", "Import"), ("export", "Export"), ("domestic", "Domestic"), ("transhipment", "Transhipment")],
        related="consignment_id.consignment_type", store=True)
    company_id = fields.Many2one("res.company", related="consignment_id.company_id")
    convey_name = fields.Char()
    lloyds_no = fields.Char()
    voyage = fields.Char()
    flight = fields.Char()
    release = fields.Char()
    shipper_ref = fields.Char()
    marks_number = fields.Char("Mark's and Numbers")
    goods_desc = fields.Char()
    freight_order_id = fields.Many2one("freight.order")
    order_package_line_ids = fields.One2many("consignment.order.package.line", "consignment_order_id")
    order_product_line_ids = fields.One2many("consignment.order.product.line", "consignment_order_id")
    order_document_line_ids = fields.One2many("consignment.order.document.line", "consignment_order_id")
    order_customs_line_ids = fields.One2many("consignment.order.customs.line", "consignment_order_id")

    def action_open_order_customs(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Consignment Order Customs",
            "res_model": "consignment.order.customs.line",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.order_customs_line_ids.ids)],
            "context": {"default_consignment_order_id": self.id}
        }

    @api.ondelete(at_uninstall=False)
    def release_freight_order(self):
        for rec in self:
            if rec.freight_order_id and rec.consignment_id:
                rec.freight_order_id.in_consignment = False
                rec.freight_order_id.consignment_id = False

    @api.model_create_multi
    def create(self, vals_list):
        rec_ids = super().create(vals_list)
        for rec_id in rec_ids:
            bill_seqs = rec_id.consignment_id.consignment_order_ids.mapped("bill_seq")
            print("bill_seqs", bill_seqs)
            if bill_seqs:
                bill_seq = max(bill_seqs)
            else:
                bill_seq = 0
            print("bill_seq", bill_seq)
            rec_id.sub_bill_no = rec_id.consignment_id.master_bill_no + "-" + str(bill_seq + 1)
            rec_id.bill_seq = bill_seq + 1
        return rec_ids


class FreightConsignmentOrderPackage(models.Model):
    _name = "consignment.order.package.line"

    consignment_order_id = fields.Many2one("freight.consignment.order")
    package_type = fields.Selection([("carton", "Carton"), ("container", "Container")])
    package_count = fields.Integer()
    weight = fields.Float()
    weight_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Weight')]")
    volume = fields.Float()
    volume_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Volume')]")
    container_no = fields.Char()
    container_type = fields.Selection(
        [("Dry_Cargo", "Dry Cargo"), ("Open_Top", "Open Top(in gauge)"),
         ("Refrigerated_ISO", "Refrigerated ISO"), ("Flat_Rack", "Flat Rack"), ("Tunnel_Container", "Tunnel Container"),
         ("Open_side_storage", "Open Side Storage"), ("Double_doors_Container", "Double Doors Container"),
         ("Insulated_or_thermal", "Insulated or Thermal"), ("Cargo_Storage_roll", "Cargo Storage Roll"),
         ("Special_purpose", "Special Purpose")])
    container_weight = fields.Float()
    container_weight_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Weight')]")
    container_gross_weight = fields.Float()
    container_gross_weight_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Weight')]")
    temperature = fields.Float()
    air_flow = fields.Integer()
    seal_no = fields.Char()
    marks = fields.Char()
    description = fields.Text()
    packing_material = fields.Text()


class FreightConsignmentOrderProduct(models.Model):
    _name = "consignment.order.product.line"
    _rec_name = "product_name"

    consignment_order_id = fields.Many2one("freight.consignment.order")
    product_name = fields.Char()
    brand = fields.Char()
    supplier = fields.Char()
    country_of_origin_id = fields.Many2one("res.country")
    country_of_import_id = fields.Many2one("res.country")
    country_of_export_id = fields.Many2one("res.country")
    invoice_number = fields.Char()
    invoice_total = fields.Float()
    currency_id = fields.Many2one("res.currency")
    exchange_rate = fields.Float()
    quantity = fields.Integer()
    qty_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Unit')]")
    weight = fields.Float()
    weight_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Weight')]")
    volume = fields.Float()
    volume_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Volume')]")
    description = fields.Text()
    packing_material = fields.Text()

    @api.onchange("currency_id")
    def set_inv_curr_rate(self):
        if self.currency_id:
            self.exchange_rate = self.currency_id.rate


class FreightConsignmentOrderDocument(models.Model):
    _name = "consignment.order.document.line"

    consignment_order_id = fields.Many2one("freight.consignment.order")
    consignment_id = fields.Many2one("freight.consignment")
    consignment_order_customs_id = fields.Many2one("consignment.order.customs.line")
    name = fields.Char()
    document_type_id = fields.Many2one("freight.document.type")
    file_data = fields.Binary()
    doc_description = fields.Text("Description")


class FreightConsignmentCustoms(models.Model):
    _name = "consignment.customs.line"

    consignment_id = fields.Many2one("freight.consignment")
    status = fields.Selection([("some_code", "some_code")])
    date = fields.Date(default=fields.Date.today)
    carrier = fields.Char()
    ocr_no = fields.Char(string="OCR No")
    ocr_ref_no = fields.Char(string="OCR Ref No")
    consolidator_name = fields.Char()
    goods_location = fields.Char()
    message_type = fields.Selection([("replacement", "Replacement"), ("cancel", "Cancel")])
    additional_info = fields.Text()
    override_reason = fields.Text()
    change_reason = fields.Text()


class FreightConsignmentOrderCustoms(models.Model):
    _name = "consignment.order.customs.line"
    _rec_name = "exporter_code"

    consignment_order_id = fields.Many2one("freight.consignment.order")
    exporter_code = fields.Char(required=True)
    delivery_authority = fields.Char()
    invoice_no = fields.Char()
    term = fields.Selection([("some_term", "some_term")])
    invoice_amount = fields.Monetary(currency_field='invoice_currency_id')
    invoice_currency_id = fields.Many2one("res.currency")
    invoice_amount_local = fields.Monetary(string="Invoice Amount (Converted)")
    currency_id = fields.Many2one("res.currency")
    invoice_currency_rate = fields.Float()
    freight_amount = fields.Monetary(currency_field="freight_currency_id")
    freight_currency_id = fields.Many2one("res.currency")
    freight_amount_local = fields.Monetary(string="Freight Amount (Converted)")
    freight_currency_rate = fields.Float()
    insurance_amount = fields.Monetary(currency_field="insurance_currency_id")
    insurance_currency_id = fields.Many2one("res.currency")
    insurance_amount_local = fields.Monetary(string="Insurance Amount (Converted)")
    insurance_currency_rate = fields.Float()
    foreign_freight_amount = fields.Monetary()
    commission_amount = fields.Monetary()
    land_charges_amount = fields.Monetary()
    other_amount = fields.Monetary(string="Other (Ded) Amount")
    levy = fields.Monetary()
    packaging_cost_amount = fields.Monetary()
    discount_amount = fields.Monetary()
    other_add_amount = fields.Monetary(string="Other (Add) Amount")
    duty = fields.Monetary()
    total = fields.Monetary()
    process_port = fields.Char()
    controlled_area = fields.Char()
    sold_consigned = fields.Selection([("sold", "Sold"), ("consigned", "Consigned")])
    total_kgs = fields.Float()
    origin_country_id = fields.Many2one("res.country")
    destination_country_id = fields.Many2one("res.country")
    no_of_packs = fields.Float()
    pack_uom_id = fields.Many2one("uom.uom", string="Packs Unit")
    message_type = fields.Selection(
        [("replace_heading", "Replace Heading"), ("replace_line", "Replace Line"), ("withdrawal", "Withdrawal"),
         ("original", "Original"), ("Replacement", "Replacement")])
    tie = fields.Char(string="T.I.E")
    lou = fields.Char(string="L.O.U")
    mou = fields.Char(string="M.O.U")
    nature_of_transaction = fields.Selection([("nature_of_transaction", "nature_of_transaction")])
    override_reason = fields.Text()
    order_customs_invoice_ids = fields.One2many("consignment.order.customs.com.inv", "consignment_order_customs_id")
    order_customs_document_line_ids = fields.One2many("consignment.order.document.line", "consignment_order_customs_id")

    @api.onchange("invoice_currency_id")
    def set_inv_curr_rate(self):
        if self.invoice_currency_id:
            self.invoice_currency_rate = self.invoice_currency_id.rate

    @api.onchange("freight_currency_id")
    def set_fre_curr_rate(self):
        if self.freight_currency_id:
            self.freight_currency_rate = self.freight_currency_id.rate

    @api.onchange("insurance_currency_id")
    def set_ins_curr_rate(self):
        if self.insurance_currency_id:
            self.insurance_currency_rate = self.insurance_currency_id.rate

    def action_open_order_customs_invoice(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Commercial Invoices",
            "res_model": "consignment.order.customs.com.inv",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.order_customs_invoice_ids.ids)],
            "context": {"default_consignment_order_id": self.consignment_order_id.id}
        }


class ConOrdersCustomsCommercialInvoice(models.Model):
    _name = "consignment.order.customs.com.inv"

    consignment_order_customs_id = fields.Many2one("consignment.order.customs.line")
    consignment_order_id = fields.Many2one("freight.consignment.order")
    invoice_no = fields.Char()
    term = fields.Selection([("some_term", "some_term")])
    amount = fields.Float()
    line_total = fields.Float(compute="compute_amount")
    balance = fields.Float(compute="compute_amount")
    invoice_line_ids = fields.One2many("customs.com.inv.line", "invoice_id")

    def compute_amount(self):
        for rec in self:
            rec.line_total = 2
            rec.balance = 2


class CustomsComInvLine(models.Model):
    _name = "customs.com.inv.line"

    invoice_id = fields.Many2one("consignment.order.customs.com.inv")
    product_name = fields.Char()
    consignment_order_id = fields.Many2one("freight.consignment.order", compute="_compute_consignment_order_id",
                                           store=True, precompute=True)
    order_product_id = fields.Many2one("consignment.order.product.line",
                                       domain="[('consignment_order_id', '=', consignment_order_id)]")
    price = fields.Float(related="order_product_id.invoice_total")
    invoice_quantity = fields.Integer()
    invoice_qty_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Unit')]")
    customs_quantity = fields.Integer()
    customs_qty_uom_id = fields.Many2one("uom.uom", domain="[('category_id.name', '=', 'Unit')]")
    country_of_origin_id = fields.Many2one("res.country", string="Origin Country", related="order_product_id.country_of_origin_id")
    tariff = fields.Char()
    amount_fob_f = fields.Float(string="Amount FOB(F)")
    amount_fob = fields.Float(string="Amount FOB")
    permits = fields.Selection([("permits", "permits")])
    other_info = fields.Selection([("other_info", "other_info")])
    gross_wright = fields.Float("Gross Weight(kg)")
    net_wright = fields.Float("Net Weight(kg)")
    packages = fields.Float()
    pack_type_id = fields.Many2one("uom.uom")
    shipping_marks = fields.Char()
    m_3 = fields.Float(string="M3")
    description = fields.Text(related="order_product_id.description")

    @api.depends("product_name")
    def _compute_consignment_order_id(self):
        for rec in self:
            rec.consignment_order_id = rec.invoice_id.consignment_order_id.id
