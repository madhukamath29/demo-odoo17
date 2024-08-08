import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportJournal(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_journal'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Journal Audit Report'

    def lines(self, target_move, journal_ids, sort_selection, data):
        if isinstance(journal_ids, int):
            journal_ids = [journal_ids]

        move_state = ['draft', 'posted']
        if target_move == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_ids)] + query_get_clause[2]
        query = 'SELECT "account_move_line".id FROM ' + query_get_clause[0] + ', account_move am, account_account acc WHERE "account_move_line".account_id = acc.id AND "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ORDER BY '
        if sort_selection == 'date':
            query += '"account_move_line".date'
        else:
            query += 'am.name'
        query += ', "account_move_line".move_id, acc.code'
        self.env.cr.execute(query, tuple(params))
        ids = (x[0] for x in self.env.cr.fetchall())
        return self.env['account.move.line'].browse(ids)

    def _sum_debit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(debit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    def _sum_credit(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        self.env.cr.execute('SELECT SUM(credit) FROM ' + query_get_clause[0] + ', account_move am '
                        'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' ',
                        tuple(params))
        return self.env.cr.fetchone()[0] or 0.0

    def _get_taxes(self, data, journal_id):
        move_state = ['draft', 'posted']
        if data['form'].get('target_move', 'all') == 'posted':
            move_state = ['posted']

        query_get_clause = self._get_query_get_clause(data)
        params = [tuple(move_state), tuple(journal_id.ids)] + query_get_clause[2]
        query = """
            SELECT rel.account_tax_id, SUM("account_move_line".balance) AS base_amount
            FROM account_move_line_account_tax_rel rel, """ + query_get_clause[0] + """ 
            LEFT JOIN account_move am ON "account_move_line".move_id = am.id
            WHERE "account_move_line".id = rel.account_move_line_id
                AND am.state IN %s
                AND "account_move_line".journal_id IN %s
                AND """ + query_get_clause[1] + """
           GROUP BY rel.account_tax_id"""
        self.env.cr.execute(query, tuple(params))
        ids = []
        base_amounts = {}
        for row in self.env.cr.fetchall():
            ids.append(row[0])
            base_amounts[row[0]] = row[1]


        res = {}
        for tax in self.env['account.tax'].browse(ids):
            self.env.cr.execute('SELECT sum(debit - credit) FROM ' + query_get_clause[0] + ', account_move am '
                'WHERE "account_move_line".move_id=am.id AND am.state IN %s AND "account_move_line".journal_id IN %s AND ' + query_get_clause[1] + ' AND tax_line_id = %s',
                tuple(params + [tax.id]))
            res[tax] = {
                'base_amount': base_amounts[tax.id],
                'tax_amount': self.env.cr.fetchone()[0] or 0.0,
            }
            if journal_id.type == 'sale':
                #sales operation are credits
                res[tax]['base_amount'] = res[tax]['base_amount'] * -1
                res[tax]['tax_amount'] = res[tax]['tax_amount'] * -1
        return res

    def _get_query_get_clause(self, data):
        return self.env['account.move.line'].with_context(data['form'].get('used_context', {}))._query_get()

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        target_move = data['form'].get('target_move', 'all')
        sort_selection = data['form'].get('sort_selection', 'date')

        res = {}
        for journal in data['form']['journal_ids']:
            res[journal] = self.with_context(data['form'].get('used_context', {})).lines(target_move, journal, sort_selection, data)
        return {
            'doc_ids': data['form']['journal_ids'],
            'doc_model': self.env['account.journal'],
            'data': data,
            'docs': self.env['account.journal'].browse(data['form']['journal_ids']),
            'time': time,
            'lines': res,
            'sum_credit': self._sum_credit,
            'sum_debit': self._sum_debit,
            'get_taxes': self._get_taxes,
        }

    def generate_xlsx_report(self, workbook, data, objects):
        report_data = self._get_report_values(objects, data)
        docs = report_data['docs']
        lines = report_data['lines']
        res_company = self.env.company

        bold_format = workbook.add_format({'bold': True})
        normal_format = workbook.add_format({'bold': False})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        sheet = workbook.add_worksheet('Journal Report')
        row = 0

        for o in docs:
            sum_debit = self._sum_debit(data, o)
            sum_credit = self._sum_credit(data, o)
            get_taxes = self._get_taxes(data, o)

            sheet.write(row, 0, f"{o.name} Journal", bold_format)
            row += 1
            sheet.write(row, 0, 'Company:', bold_format)
            sheet.write(row, 1, res_company.name)
            row += 1

            sheet.write(row, 0, 'Journal:', bold_format)
            sheet.write(row, 1, o.name)
            row += 1

            sheet.write(row, 0, 'Entries Sorted By:', bold_format)
            sort_selection = data['form'].get('sort_selection')
            sort_label = 'Journal Entry Number' if sort_selection != 'l.date' else 'Date'
            sheet.write(row, 1, sort_label)
            row += 1

            sheet.write(row, 0, 'Target Moves:', bold_format)
            target_move = data['form'].get('target_move', 'all')
            target_move_label = 'All Entries' if target_move == 'all' else 'All Posted Entries'
            sheet.write(row, 1, target_move_label)
            row += 1

            headers = ['Move', 'Date', 'Account', 'Partner', 'Label', 'Debit', 'Credit']
            if data['form'].get('amount_currency'):
                headers.append('Currency')
            for col, header in enumerate(headers):
                sheet.write(row, col, header, bold_format)
            row += 1

            for aml in lines.get(o.id, []):
                sheet.write(row, 0,
                            aml['move_id']['name'] if aml['move_id']['name'] != '/' else f"*{aml['move_id']['id']}")
                sheet.write(row, 1, aml['date'], date_format)
                sheet.write(row, 2, aml['account_id']['code'])
                sheet.write(row, 3, aml['partner_id']['name'][:23] if aml['partner_id'] else '')
                sheet.write(row, 4, aml['name'][:35] if aml['name'] else '')
                sheet.write(row, 5, aml['debit'], currency_format)
                sheet.write(row, 6, aml['credit'], currency_format)
                if data['form'].get('amount_currency') and aml.get('amount_currency'):
                    sheet.write(row, 7, aml['amount_currency'], currency_format)
                row += 1

            row += 1
            sheet.write(row, 0, 'Total', bold_format)
            sheet.write(row, 5, sum_debit, currency_format)
            sheet.write(row, 6, sum_credit, currency_format)
            row += 2

            sheet.write(row, 0, 'Tax Declaration', bold_format)
            row += 1
            tax_headers = ['Name', 'Base Amount', 'Tax Amount']
            for col, header in enumerate(tax_headers):
                sheet.write(row, col, header, bold_format)
            row += 1

            for tax in get_taxes:
                sheet.write(row, 0, tax['name'])
                sheet.write(row, 1, get_taxes[tax]['base_amount'], currency_format)
                sheet.write(row, 2, get_taxes[tax]['tax_amount'], currency_format)
                row += 1
            row += 1
