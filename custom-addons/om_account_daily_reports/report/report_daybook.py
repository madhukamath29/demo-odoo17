# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime


class ReportDayBook(models.AbstractModel):
    _name = 'report.om_account_daily_reports.report_daybook'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Day Book'

    def _get_account_move_entry(self, accounts, form_data, date):
        cr = self.env.cr
        MoveLine = self.env['account.move.line']
        init_wheres = [""]

        init_tables, init_where_clause, init_where_params =MoveLine._query_get()
        if init_where_clause.strip():
            init_wheres.append(init_where_clause.strip())
        if form_data['target_move'] == 'posted':
            target_move = "AND m.state = 'posted'"
        else:
            target_move = ''

        sql = ("""
                    SELECT 0 AS lid, 
                          l.account_id AS account_id, l.date AS ldate, j.code AS lcode, 
                          l.amount_currency AS amount_currency,l.ref AS lref,l.name AS lname, 
                          COALESCE(SUM(l.credit),0.0) AS credit,COALESCE(l.debit,0) AS debit,COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit),0) as balance, 
                              m.name AS move_name, 
                              c.symbol AS currency_code, 
                              p.name AS lpartner_id, 
                              m.id AS mmove_id 
                            FROM 
                              account_move_line l 
                              LEFT JOIN account_move m ON (l.move_id = m.id) 
                              LEFT JOIN res_currency c ON (l.currency_id = c.id) 
                              LEFT JOIN res_partner p ON (l.partner_id = p.id) 
                              JOIN account_journal j ON (l.journal_id = j.id) 
                              JOIN account_account acc ON (l.account_id = acc.id) 
                            WHERE 
                              l.account_id IN %s 
                              AND l.journal_id IN %s """ + target_move + """ 
                              AND l.date = %s 
                            GROUP BY 
                              l.id, 
                              l.account_id, 
                              l.date, 
                              m.name, 
                              m.id, 
                              p.name, 
                              c.symbol, 
                              j.code, 
                              l.ref 
                            ORDER BY 
                              l.date DESC
                     """)

        where_params = (tuple(accounts.ids), tuple(form_data['journal_ids']), date)
        cr.execute(sql, where_params)
        data = cr.dictfetchall()
        res = {}
        debit = credit = balance = 0.00
        for line in data:
            debit += line['debit']
            credit += line['credit']
            balance += line['balance']
        res['debit'] = debit
        res['credit'] = credit
        res['balance'] = balance
        res['lines'] = data
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        form_data = data['form']

        date_from = datetime.strptime(form_data['date_from'],
                                       '%Y-%m-%d').date()
        date_to = datetime.strptime(form_data['date_to'], '%Y-%m-%d').date()
        codes = []

        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search([('id', 'in', data['form']['journal_ids'])])]
        accounts = self.env['account.account'].search([])
        dates = []
        record = []
        days_total = date_to - date_from
        for day in range(days_total.days + 1):
            dates.append(date_from + timedelta(days=day))
        for date in dates:
            date_data = str(date)
            accounts_res = self.with_context(data['form'].get('comparison_context', {}))._get_account_move_entry(accounts, form_data, date_data)
            if accounts_res['lines']:
                record.append({
                    'date': date,
                    'debit': accounts_res['debit'],
                    'credit': accounts_res['credit'],
                    'balance': accounts_res['balance'],
                    'move_lines': accounts_res['lines']
                })
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': record,
            'print_journal': codes,
        }

    def generate_xlsx_report(self, workbook, data, objs):
        report_data = self._get_report_values(None, data)
        user = self.env.user
        res_company = self.env.company
        form_data = report_data.get('data', {})
        print_journal = ', '.join(report_data.get('print_journal', []))
        date_from = form_data.get('date_from', '')
        date_to = form_data.get('date_to', '')
        target_move = form_data.get('target_move', 'all')
        accounts = report_data.get('Accounts', [])

        header_format = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': res_company.currency_id.symbol + '#,##0.00'})
        title_currency_format = workbook.add_format({'num_format':  res_company.currency_id.symbol + '#,##0.00',
                                                     'bold': True})

        sheet = workbook.add_worksheet('Day Book')
        sheet.merge_range('A1:J1', 'Account Day Book', header_format)

        sheet.write('A3', 'Journals:', header_format)
        sheet.write('B3', print_journal)
        sheet.write('A4', 'Start Date:', header_format)
        sheet.write('B4', date_from)
        sheet.write('A5', 'End Date:', header_format)
        sheet.write('B5', date_to)
        sheet.write('A6', 'Target Moves:', header_format)
        sheet.write('B6', 'All Entries' if target_move == 'all' else 'Posted Entries')

        headers = (['Date', 'JRNL', 'Partner', 'Ref', 'Move', 'Entry Label', 'Debit', 'Credit', 'Balance'] +
                   (['Currency'] if user.has_group('base.group_multi_currency') else []))
        for col_num, header in enumerate(headers):
            sheet.write(8, col_num, header, header_format)

        row = 9
        for account in accounts:
            sheet.write(row, 0, str(account['date']), header_format)
            sheet.write(row, 6, account['debit'], title_currency_format)
            sheet.write(row, 7, account['credit'], title_currency_format)
            sheet.write(row, 8, account['balance'], title_currency_format)
            row += 1

            for line in account['move_lines']:
                sheet.write(row, 0, str(line['ldate']))
                sheet.write(row, 1, line['lcode'])
                sheet.write(row, 2, line['lpartner_id'])
                sheet.write(row, 3, line['lref'])
                sheet.write(row, 4, line['move_name'])
                sheet.write(row, 5, line['lname'])
                sheet.write(row, 6, line['debit'], money_format)
                sheet.write(row, 7, line['credit'], money_format)
                sheet.write(row, 8, line['balance'], money_format)
                if (user.has_group('base.group_multi_currency') and
                        (line['amount_currency'] and line['amount_currency'] > 0.00)):
                    sheet.write(row, 9, f"{line['amount_currency']} {line['currency_code']}")
                row += 1
