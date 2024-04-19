from odoo import http
from odoo.http import request


class Websitefreightorder(http.Controller):

    @http.route('/', type='http', auth="public", website=True)
    def submit_freight_order_page(self, **kwargs):
        # Fetch records from the required models
        shipper_ids = request.env['res.partner'].search([])
        receiver_ids = request.env['res.partner'].search(
            [])  # You can customize this query as needed
        bill_to_ids = request.env['res.partner'].search(
            [])  # You can customize this query as needed
        notify_party_ids = request.env['res.partner'].search(
            [])  # You can customize this query as needed
        origin_port_ids = request.env['port'].search([])
        destination_port_ids = request.env['port'].search([])
        consignment_type_ids = request.env['consignment.type'].search([])
        transport_type_ids = request.env['transport.type'].search([])
        mode_ids = request.env['mode'].search([])
        company_ids = request.env['res.company'].search([])
        status_ids = request.env['freight.order.status'].search([])

        # Pass fetched records to the template context
        return request.render("inv_freight_management.freight_order_page_template", {
            'shipper_ids': shipper_ids,
            'receiver_ids': receiver_ids,
            'bill_to_ids': bill_to_ids,
            'notify_party_ids': notify_party_ids,
            'origin_port_ids': origin_port_ids,
            'destination_port_ids': destination_port_ids,
            'consignment_type_ids': consignment_type_ids,
            'transport_type_ids': transport_type_ids,
            'mode_ids': mode_ids,
            'company_ids': company_ids,
            'status_ids': status_ids,
        })

    @http.route('/submit_freight_order', type='http', auth="public", website=True, csrf=False)
    def submit_freight_order(self, **kwargs):
        # Fetch form data
        name = kwargs.get('name')
        order_date = kwargs.get('order_date')
        ready_date = kwargs.get('ready_date')
        tracking_no = kwargs.get('tracking_no')
        term = kwargs.get('term')
        shipper_id = kwargs.get('shipper_id')
        receiver_id = kwargs.get('receiver_id')
        bill_to_id = kwargs.get('bill_to_id')
        notify_party_id = kwargs.get('notify_party_id')
        origin_port_id = kwargs.get('origin_port_id')
        destination_port_id = kwargs.get('destination_port_id')
        consignment_type_id = kwargs.get('consignment_type_id')
        transport_type_id = kwargs.get('transport_type_id')
        mode_id = kwargs.get('mode_id')
        company_id = kwargs.get('company_id')
        shipping_date = kwargs.get('shipping_date')
        status_id = kwargs.get('status_id')
        notes = kwargs.get('notes')

        # Create a new record of inv.freightorder
        order_vals = {
            'name': name,
            'order_date': order_date,
            'ready_date': ready_date,
            'tracking_no': tracking_no,
            'term': term,
            'shipper_id': int(shipper_id),
            'receiver_id': int(receiver_id),
            'bill_to_id': int(bill_to_id),
            'notify_party_id': int(notify_party_id),
            'origin_port_id': int(origin_port_id),
            'destination_port_id': int(destination_port_id),
            'consignment_type_id': int(consignment_type_id),
            'transport_type_id': int(transport_type_id),
            'mode_id': int(mode_id),
            'company_id': int(company_id),
            'shipping_date': shipping_date,
            'status_id': int(status_id),
            'notes': notes,
        }

        # Create a new record of inv.freightorder with sudo() to bypass access control
        new_order = request.env['inv.freightorder'].sudo().create(order_vals)

        # Redirect to a thank you page or homepage after form submission
        return request.render('inv_freight_management.thank_you_page')
