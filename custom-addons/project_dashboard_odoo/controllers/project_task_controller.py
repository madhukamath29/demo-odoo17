from odoo import http
from odoo.http import request
from datetime import datetime, timedelta


class ProjectTaskController(http.Controller):

    @http.route('/project/task/count', type='json', auth='user')
    def project_task_count(self, filter):
        # Get the current date
        today = datetime.today()

        # Determine the date range based on the filter
        if filter == "last_10_days":
            start_date = today - timedelta(days=10)
        elif filter == "last_30_days":
            start_date = today - timedelta(days=30)
        elif filter == "last_3_month":
            start_date = today - timedelta(days=90)
        elif filter == "last_year":
            start_date = today - timedelta(days=365)
        else:
            start_date = None

        # Fetch the tasks based on the date range
        domain = []
        if start_date:
            domain.append(('date_start', '>=', start_date))

        tasks = request.env['project.task'].search(domain)

        # Process the tasks data to return to the frontend
        project_task_data = {
            "project": [task.project_id.name for task in tasks],
            "color": ["#FF6384", "#36A2EB", "#FFCE56"],
            "task": [task.id for task in tasks]
        }

        return project_task_data
