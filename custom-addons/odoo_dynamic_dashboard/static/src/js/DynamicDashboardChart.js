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

                if (!x_axis || !y_axis) {
                    console.error('x_axis or y_axis is undefined:', { x_axis, y_axis });
                    return;
                }

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
        try {
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
                    startDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 3, 1);
                    break;
                case 'last_year':
                    startDate = new Date(currentDate.getFullYear() - 1, currentDate.getMonth(), 1);
                    break;
                default:
                    startDate = new Date();
                    break;
            }

            const formatDate = date => date.toISOString().split('T')[0];
            const formatMonth = date => date.toLocaleString('default', { month: 'long' }) + ' ' + date.getFullYear();

            const x_axis = [];
            if (filterType === 'last_3_months' || filterType === 'last_year') {
                // Generate x_axis for months
                let current = new Date(startDate.getFullYear(), startDate.getMonth(), 1);
                while (current <= currentDate) {
                    x_axis.push(formatMonth(current));
                    current.setMonth(current.getMonth() + 1);
                }
            } else {
                // Generate x_axis for days
                let current = new Date(startDate);
                while (current <= currentDate) {
                    x_axis.push(formatDate(current));
                    current.setDate(current.getDate() + 1);
                }
            }

            // Fetch data from an actual data source
            const configurationModel = this.props.configurationModel; // Assumes configuration model is passed as a prop
            if (!configurationModel) {
                throw new Error("Configuration model is not provided");
            }
            console.log('Configuration model:', configurationModel);

            const data = await this.fetchDataFromSource(configurationModel, startDate, currentDate, filterType);

            // Update x_axis and y_axis based on the fetched data
            this.props.widget.x_axis = x_axis;
            this.props.widget.y_axis = data.map(item => item.value); // Assuming data contains 'value' field

            // Re-render the chart with the new data
            this.renderChart();
        } catch (error) {
            console.error('Error in fetchData:', error);
        }
    }

    async fetchDataFromSource(configurationModel, startDate, endDate, filterType) {
        try {
            console.log(`Fetching data from source with configuration: ${JSON.stringify(configurationModel)}`);
            const modelId = configurationModel.model_id;
            const measuredField = configurationModel.measured_field;
            const groupBy = configurationModel.group_by;

            if (!modelId || !measuredField || !groupBy) {
                throw new Error("Configuration model is missing required fields");
            }
            const apiUrl = `https://api.example.com/data`;
            const params = {
                model_id: modelId,
                measured_field: measuredField,
                group_by: groupBy,
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString(),
                aggregate_by: (filterType === 'last_3_months' || filterType === 'last_year') ? 'month' : 'day'
            };

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(params)
            });

            if (!response.ok) {
                throw new Error(`Error fetching data: ${response.statusText}`);
            }

            const data = await response.json();
            return data; // Ensure the data format matches your requirements
        } catch (error) {
            console.error('Error in fetchDataFromSource:', error);
            return [];
        }
    }
}

DynamicDashboardChart.template = xml`
<div style="padding-bottom: 30px" t-att-class="this.props.widget.cols + ' col-4 block'" t-att-data-id="this.props.widget.id">
    <div class="card">
        <div class="card-header">
            <div class="row align-items-center">
                <div class="col">
                    <h3><t t-esc="this.props.widget.name"/></h3>
                </div>
                <div class="col text-right" style="display:flex">
                    <!-- Chart type buttons -->
                    <div class="chart-buttons" style="display:flex">
                        <button t-on-click="downloadDetails" class="button-34" role="button" style="background-color: #007bff; margin-right: 10px; height: 30px; width:50px;">
                            <i class="fa fa-download" style="color: white; display:flex;"></i>
                        </button>
                        <button t-on-click="() => this.changeChartType('bar')" class="button-34" role="button" style="background-color: #007bff; margin-right: 10px; height: 30px; width:50px;">
                            <i class="fa fa-bar-chart" style="color: white; display:flex;"></i>
                        </button>
                        <button t-on-click="() => this.changeChartType('line')" class="button-34" role="button" style="background-color: #007bff; margin-right: 10px; height: 30px; width:50px;">
                            <i class="fa fa-line-chart" style="color: white; display:flex;"></i>
                        </button>
                        <button t-on-click="() => this.changeChartType('pie')" class="button-34" role="button" style="background-color: #007bff; margin-right: 10px; height: 30px; width:50px;">
                            <i class="fa fa-pie-chart" style="color: white; display:flex;"></i>
                        </button>
                        <button t-on-click="() => this.changeChartType('doughnut')" class="button-34" role="button" style="background-color: #007bff; margin-right: 10px; height: 30px; width:50px;">
                            <i class="fa fa-circle-thin" style="color: white; display:flex;"></i>
                        </button>
                        <button t-on-click="() => this.changeChartType('radar')" class="button-34" role="button" style="background-color: #007bff; height: 30px; width:50px;">
                            <i class="fa fa-bullseye" style="color: white; display:flex;"></i>
                        </button>
                    </div>
                    <!-- End chart type buttons -->
                </div>
            </div>
        </div>
        <div class="card-body" id="in_ex_body_hide">
            <div class="row">
                <div class="col-md-12 chart_canvas">
                    <select id="data_filter_selection" t-on-change="onchangeFilter">
                        <option value="last_10_days" selected="selected">Last 10 Days</option>
                        <option value="last_30_days">Last 30 Days</option>
                        <option value="last_3_months">Last 3 Months</option>
                        <option value="last_year">Last Year</option>
                    </select>
                    <canvas t-ref="chart" style="width: 100%"></canvas>
                </div>
            </div>
        </div>
    </div>
</div>
`;


DynamicDashboardChart.components = {};
registry.category("components").add("DynamicDashboardChart", DynamicDashboardChart);

export default DynamicDashboardChart;
