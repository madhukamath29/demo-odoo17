/** @odoo-module */

import { registry } from '@web/core/registry';
import { loadJS } from '@web/core/assets';
import { getColor } from "@web/core/colors/colors";
const { Component, xml, onWillStart, useRef, useState, onMounted } = owl;

export class DynamicDashboardChart extends Component {
    setup() {
        // Ensure doAction is passed correctly
        if (!this.props.doAction) {
            console.error('doAction is not defined in props');
            return;
        }

        this.doAction = this.props.doAction;
        this.chartRef = useRef("chart");
        this.chartInstance = null;
        this.state = useState({
            filterType: 'last_10_days'  // default filter
        });

        // Bind methods to ensure correct context
        this.changeChartType = this.changeChartType.bind(this);
        this.getConfiguration = this.getConfiguration.bind(this);
        this.downloadDetails = this.downloadDetails.bind(this);
        this.onchangeFilter = this.onchangeFilter.bind(this);

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.5.0/chart.min.js");
        });

        onMounted(() => this.renderChart());
    }

    async changeChartType(type) {
        console.log('Changing chart type to:', type);  // Debugging line
        this.props.widget.graph_type = type;
        await this.renderChart();
    }

    async renderChart() {
        try {
            console.log('Rendering chart with type:', this.props.widget.graph_type);  // Debugging line
            if (this.props.widget.graph_type) {
                if (this.chartInstance) {
                    this.chartInstance.destroy();  // Destroy the previous chart instance if it exists
                }

                const x_axis = this.props.widget.x_axis;
                const y_axis = this.props.widget.y_axis;
                const data = x_axis.map((key, index) => ({ key, value: y_axis[index] }));

                this.chartInstance = new Chart(this.chartRef.el, {
                    type: this.props.widget.graph_type || 'bar',
                    data: {
                        labels: data.map(row => row.key),
                        datasets: [{
                            label: this.props.widget.measured_field,
                            data: data.map(row => row.value),
                            backgroundColor: data.map((_, index) => getColor(index)),
                            hoverOffset: 4
                        }]
                    },
                });
            }
        } catch (error) {
            console.error("Error rendering chart:", error);
        }
    }

    async getConfiguration() {
        try {
            const id = this.props.widget.id;
            if (!id) {
                console.error("Widget ID is missing.");
                return;
            }

            await this.doAction({
                type: 'ir.actions.act_window',
                res_model: 'dashboard.block',
                res_id: id,
                view_mode: 'form',
                views: [[false, "form"]]
            });
        } catch (error) {
            console.error("Error getting configuration:", error);
        }
    }

    async getRecord() {
        try {
            const model_name = this.props.widget.model_name;
            if (model_name) {
                // Make a request to fetch y-axis values from the dashboard.block model
                const response = await this.doAction({
                    type: 'ir.actions.act_window',
                    res_model: model_name,
                    view_mode: 'graph',
                    views: [[false, "graph"], [false, "form"]],
                });

                // Assuming the response contains the y-axis values under the key 'y_axis'
                const y_axis_data = response.data.y_axis;
                if (y_axis_data) {
                    // Update the y-axis values in the widget props
                    this.props.widget.y_axis = y_axis_data;
                    // Re-render the chart with the new data
                    this.renderChart();
                }
            }
        } catch (error) {
            console.error("Error getting record:", error);
        }
    }

    downloadDetails() {
        try {
            if (this.chartInstance) {
                const link = document.createElement('a');
                link.href = this.chartInstance.toBase64Image();
                link.download = `${this.props.widget.name}.png`;
                link.click();
            } else {
                console.error("Chart instance is not initialized.");
            }
        } catch (error) {
            console.error("Error downloading chart:", error);
        }
    }

    async onchangeFilter(event) {
        this.state.filterType = event.target.value;
        // Fetch the new data based on the selected filter
        await this.fetchData(this.state.filterType);
        // Re-render the chart with the new data
        this.renderChart();
    }

    async fetchData(filterType) {
        // Simulate fetching data based on filterType
        // Replace this with actual data fetching logic
        console.log(`Fetching data for filter: ${filterType}`);

        const currentDate = new Date();
        let startDate;

        switch (filterType) {
            case 'last_10_days':
                startDate = new Date(currentDate.getTime() - (10 * 24 * 60 * 60 * 1000));
                break;
            case 'last_30_days':
                startDate = new Date(currentDate.getTime() - (30 * 24 * 60 * 60 * 1000));
                break;
            case 'last_3_months':
                startDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 3, currentDate.getDate());
                break;
            case 'last_year':
                startDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), currentDate.getDate());
                break;
            default:
                startDate = new Date();
                break;
        }

        const formatDate = date => date.toISOString().split('T')[0];

        const x_axis = [];
        const end = formatDate(currentDate);
        let current = new Date(startDate);

        while (current <= currentDate) {
            x_axis.push(formatDate(current));
            current.setDate(current.getDate() + 1);
        }

        // Example data update
        this.props.widget.x_axis = x_axis;
        this.props.widget.y_axis = [15, 35, 60]; // You need to update y_axis according to your actual data

        // Re-render the chart with the new data
        this.renderChart();
    }
}

DynamicDashboardChart.template = xml`
<div style="padding-bottom:30px" t-att-class="this.props.widget.cols +' col-4 block'" t-att-data-id="this.props.widget.id">
    <div class="card">
        <div class="card-header">
            <div class="row">
                <div class="col">
                    <h3><t t-esc="this.props.widget.name"/></h3>
                </div>
                <div class="col">
                    <div style="float:right;">
                        <!-- Chart type buttons -->
                        <button class="btn circle-button" t-on-click="downloadDetails">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-download circle-icon"></i>
                            </div>
                        </button>
                        <button class="btn circle-button" t-on-click="() => this.changeChartType('bar')">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-bar-chart circle-icon"></i>
                            </div>
                        </button>
                        <button class="btn circle-button" t-on-click="() => this.changeChartType('line')">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-line-chart circle-icon"></i>
                            </div>
                        </button>
                        <button class="btn circle-button" t-on-click="() => this.changeChartType('pie')">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-pie-chart circle-icon"></i>
                            </div>
                        </button>
                        <button class="btn circle-button" t-on-click="() => this.changeChartType('doughnut')">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-circle-thin circle-icon"></i>
                            </div>
                        </button>
                        <button class="btn circle-button" t-on-click="() => this.changeChartType('radar')">
                            <div class="circle-base circle1 bg-primary">
                                <i class="angle_icon rounded-circle fa fa-bullseye circle-icon"></i>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-body" id="in_ex_body_hide">
            <div class="row">
                <div class="col-md-12 chart_canvas">
                    <select id="data_filter_selection" class="btn btn-primary" t-on-change="onchangeFilter">
                        <option value="last_10_days" selected="selected">Last 10 Days</option>
                        <option value="last_30_days">Last 30 Days</option>
                        <option value="last_3_months">Last 3 Months</option>
                        <option value="last_year">Last Year</option>
                    </select>
                    <canvas t-ref="chart" width="500" height="300"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>
`;

DynamicDashboardChart.styles = `
.card {
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
    background-color: #f7f7f7;
    border-bottom: 1px solid #e0e0e0;
    padding: 15px;
}

.card-body {
    padding: 20px;
}

.circle-button {
    padding: 10px;
    border: none;
    background: transparent;
    margin: 5px;
    cursor: pointer;
}

.circle-icon {
    color: white;
    font-size: 1.2em;
}

.circle-base {
    border-radius: 50%;
    width: 40px;
    height: 40px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}

.bg-primary {
    background-color: #007bff !important;
}

h3 {
    margin: 0;
    font-size: 1.5em;
    font-weight: bold;
}
`;

DynamicDashboardChart.components = {};

registry.category("web_components").add("DynamicDashboardChart", DynamicDashboardChart);
