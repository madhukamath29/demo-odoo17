import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_trialbalance'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Trial Balance Report'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, "
                   "(SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        return account_res

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if model == 'account.account' else self.env['account.account'].search([])
        context = data['form'].get('used_context')
        analytic_accounts = []
        if data['form'].get('analytic_account_ids'):
            analytic_account_ids = self.env['account.analytic.account'].browse(data['form'].get('analytic_account_ids'))
            context['analytic_account_ids'] = analytic_account_ids
            analytic_accounts = [account.name for account in analytic_account_ids]
        account_res = self.with_context(context)._get_accounts(accounts, display_account)
        codes = []
        if data['form'].get('journal_ids', False):
            codes = [journal.code for journal in
                     self.env['account.journal'].search(
                         [('id', 'in', data['form']['journal_ids'])])]
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'print_journal': codes,
            'analytic_accounts': analytic_accounts,
            'time': time,
            'Accounts': account_res,
        }

    def generate_xlsx_report(self, workbook, data, objects):
        report_data = self._get_report_values(objects, data)
        accounts = report_data['Accounts']
        res_company = self.env.company
        print_journal = report_data.get('print_journal', [])

        sheet = workbook.add_worksheet('Trial Balance')
        bold = workbook.add_format({'bold': True})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        right_align = workbook.add_format({'align': 'right'})

        sheet.write(0, 0, f"{res_company.name}: Trial Balance", bold)

        filters = data['form']
        display_account = filters.get('display_account', 'all')
        display_account_map = {
            'all': "All accounts",
            'movement': "With movements",
            'not_zero': "With balance not equal to zero"
        }
        sheet.write(2, 0, 'Display Account:', bold)
        sheet.write(2, 1, display_account_map.get(display_account, 'All accounts'))

        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        if date_from:
            sheet.write(2, 2, 'Date from:', bold)
            sheet.write(2, 3, date_from)
        if date_to:
            sheet.write(3, 2, 'Date to:', bold)
            sheet.write(3, 3, date_to)

        sheet.write(3, 0, 'Target Moves:', bold)
        target_move = filters.get('target_move', 'all')
        target_move_label = 'All Entries' if target_move == 'all' else 'All Posted Entries'
        sheet.write(3, 1, target_move_label)

        sheet.write(4, 0, 'Journals:', bold)
        sheet.write(4, 1, ', '.join(print_journal))

        if filters.get('analytic_accounts'):
            sheet.write(4, 2, 'Analytic Accounts:', bold)
            analytic_accounts = ', '.join(filters['analytic_accounts'])
            sheet.write(4, 3, analytic_accounts)

        headers = ['Code', 'Account', 'Debit', 'Credit', 'Balance']
        header_row = 6
        for col, header in enumerate(headers):
            sheet.write(header_row, col, header, bold)

        row = header_row + 1
        for account in accounts:
            sheet.write(row, 0, account['code'])
            sheet.write(row, 1, account['name'])
            sheet.write(row, 2, account['debit'], currency_format)
            sheet.write(row, 3, account['credit'], currency_format)
            sheet.write(row, 4, account['balance'], currency_format)
            row += 1
