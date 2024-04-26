from odoo import models, fields


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
    exc_rate = fields.Float(string="Exc Rate")
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
    currency = fields.Char(string='Currency')
    exc_rate_3 = fields.Float(string='Exc Rate')
    fob_fc = fields.Float(string='FOB(FC)')
    fob_lc = fields.Float(string='FOB(LC)')
    solid_consign = fields.Selection([
        ('solid', 'Solid'),
        ('consign', 'Consign'),
    ], string='Solid/Consign')
    style = fields.Char(string='Style')
    edi_date = fields.Date(string='EDI Date')
    response = fields.Char(string='Response')
