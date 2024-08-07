/** @odoo-module **/

import { ReportAction } from '@web/webclient/actions/reports/report_action';
import { patch } from "@web/core/utils/patch";


patch(ReportAction.prototype, {
    print(reportType) {
        this.action.doAction({
            type: "ir.actions.report",
            report_type: reportType,
            report_name: this.props.report_name,
            report_file: this.props.report_file,
            data: this.props.data || {},
            context: this.props.context || {},
            display_name: this.title,
        });
    }
});
