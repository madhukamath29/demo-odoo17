from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTax(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_tax'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Tax Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        return {
            'data': data['form'],
            'lines': self.get_lines(data.get('form')),
        }

    def _sql_from_amls_one(self):
        sql = """SELECT "account_move_line".tax_line_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                    FROM %s
                    WHERE %s GROUP BY "account_move_line".tax_line_id"""
        return sql

    def _sql_from_amls_two(self):
        sql = """SELECT r.account_tax_id, COALESCE(SUM("account_move_line".debit-"account_move_line".credit), 0)
                 FROM %s
                 INNER JOIN account_move_line_account_tax_rel r ON ("account_move_line".id = r.account_move_line_id)
                 INNER JOIN account_tax t ON (r.account_tax_id = t.id)
                 WHERE %s GROUP BY r.account_tax_id"""
        return sql

    def _compute_from_amls(self, options, taxes):
        #compute the tax amount
        sql = self._sql_from_amls_one()
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        query = sql % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['tax'] = abs(result[1])

        #compute the net amount
        sql2 = self._sql_from_amls_two()
        query = sql2 % (tables, where_clause)
        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        for result in results:
            if result[0] in taxes:
                taxes[result[0]]['net'] = abs(result[1])

    @api.model
    def get_lines(self, options):
        taxes = {}
        for tax in self.env['account.tax'].search([('type_tax_use', '!=', 'none')]):
            if tax.children_tax_ids:
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    taxes[child.id] = {'tax': 0, 'net': 0, 'name': child.name, 'type': tax.type_tax_use}
            else:
                taxes[tax.id] = {'tax': 0, 'net': 0, 'name': tax.name, 'type': tax.type_tax_use}
        self.with_context(date_from=options['date_from'], date_to=options['date_to'],
                          state=options['target_move'],
                          strict_range=True)._compute_from_amls(options, taxes)
        groups = dict((tp, []) for tp in ['sale', 'purchase'])
        for tax in taxes.values():
            if tax['tax']:
                groups[tax['type']].append(tax)
        return groups

    def generate_xlsx_report(self, workbook, data, docs):
        report_data = self._get_report_values(None, data)

        form_data = report_data.get('data', {})
        lines = report_data.get('lines', {})

        sheet = workbook.add_worksheet('Tax Report')

        bold_format = workbook.add_format({'bold': True})
        normal_format = workbook.add_format({'bold': False})
        monetary_format = workbook.add_format({'num_format': '#,##0.00'})
        res_company = self.env.company

        sheet.write('A1', 'Tax Report', bold_format)

        sheet.write('A3', 'Company:', bold_format)
        sheet.write('B3', docs[0].company_id.name, normal_format)

        if form_data.get('date_from'):
            sheet.write('A4', 'Date from:', bold_format)
            sheet.write('B4', form_data['date_from'], normal_format)

        if form_data.get('date_to'):
            sheet.write('A5', 'Date to:', bold_format)
            sheet.write('B5', form_data['date_to'], normal_format)

        sheet.write('A6', 'Target Moves:', bold_format)
        target_move = 'All Entries' if form_data.get('target_move') == 'all' else 'All Posted Entries'
        sheet.write('B6', target_move, normal_format)

        start_row = 8
        sheet.write(start_row, 0, 'Sale', bold_format)
        sheet.write(start_row, 1, 'Net', bold_format)
        sheet.write(start_row, 2, 'Tax', bold_format)
        start_row += 1

        for line in lines.get('sale', []):
            sheet.write(start_row, 0, line.get('name', ''), normal_format)
            sheet.write(start_row, 1, f"{res_company.currency_id.symbol} {line.get('net', 0.0)}", monetary_format)
            sheet.write(start_row, 2, f"{res_company.currency_id.symbol} {line.get('tax', 0.0)}", monetary_format)
            start_row += 1

        sheet.write(start_row, 0, 'Purchase', bold_format)
        start_row += 1

        for line in lines.get('purchase', []):
            sheet.write(start_row, 0, line.get('name', ''), normal_format)
            sheet.write(start_row, 1, f"{res_company.currency_id.symbol} {line.get('net', 0.0)}", monetary_format)
            sheet.write(start_row, 2, f"{res_company.currency_id.symbol} {line.get('tax', 0.0)}", monetary_format)
            start_row += 1
