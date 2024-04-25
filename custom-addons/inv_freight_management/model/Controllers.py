from odoo import http
from odoo.http import request


class DocumentPreviewController(http.Controller):

    @http.route('/document/preview/<int:document_id>', type='http', auth="user")
    def document_preview(self, document_id, **kw):
        document = request.env['consignment.document'].browse(document_id)
        return request.render('your_module_name.document_preview_template', {'document': document})