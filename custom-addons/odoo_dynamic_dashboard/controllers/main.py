from odoo import http
from odoo.http import request
import io
import xlsxwriter


class DynamicDashboardController(http.Controller):

    @http.route('/dynamic_dashboard/download_details', type='http', auth='user', methods=['GET'])
    def download_details(self, model_name):
        records = request.env[model_name].search_read([], [])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Write the headers
        headers = records[0].keys() if records else []
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Write the data
        for row_num, record in enumerate(records, 1):
            for col_num, (key, value) in enumerate(record.items()):
                worksheet.write(row_num, col_num, value)

        workbook.close()
        output.seek(0)

        headers = [
            ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
            ('Content-Disposition', f'attachment; filename={model_name}_details.xlsx;')
        ]

        return request.make_response(output.getvalue(), headers)
