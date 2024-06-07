//  /** @odoo-module */

//  import { registry } from '@web/core/registry';
//  import { DynamicDashboardTile } from './DynamicDashboardTile';
//  import { DynamicDashboardChart } from './DynamicDashboardChart';
//  import { useService } from "@web/core/utils/hooks";
//  const { Component, mount } = owl;

//  export class DynamicDashboard extends Component {
//      setup() {
//          this.actionService = useService("action");
//          this.rpc = this.env.services.rpc;
//          this.renderDashboard = this.renderDashboard.bind(this);
//          this._onClick_add_block = this._onClick_add_block.bind(this);

//          this.renderDashboard();
//      }

//      async renderDashboard() {
//          const actionService = this.actionService;
//          const rpc = this.rpc;
//          try {
//              const response = await this.rpc('/get/values', {'action_id': this.props.actionId});
//              console.log('Received response:', response);
//              if ($('.o_dynamic_dashboard')[0]) {
//                  for (let i = 0; i < response.length; i++) {
//                      console.log('Mounting component for:', response[i]);
//                      if (response[i].type === 'tile') {
//                          mount(DynamicDashboardTile, $('.o_dynamic_tile')[0], { props: {
//                              widget: response[i], doAction: actionService.doAction
//                          }});
//                      } else {
//                          mount(DynamicDashboardChart, $('.o_dynamic_graph')[0], { props: {
//                              widget: response[i], doAction: actionService.doAction, rpc: rpc
//                          }});
//                      }
//                  }
//              }
//          } catch (error) {
//              console.error("Error rendering dashboard:", error);
//          }
//      }

//      async _onClick_add_block(e) {
//          const type = $(e.target).attr('data-type');
//          try {
//              const response = await this.rpc('/create/tile', {'type': type, 'action_id': this.props.actionId});
//              console.log('Response from add block:', response);
//              if (response.type === 'tile') {
//                  mount(DynamicDashboardTile, $('.o_dynamic_tile')[0], { props: {
//                      widget: response, doAction: this.actionService.doAction
//                  }});
//              } else {
//                  mount(DynamicDashboardChart, $('.o_dynamic_graph')[0], { props: {
//                      widget: response, doAction: this.actionService.doAction
//                  }});
//              }
//          } catch (error) {
//              console.error("Error adding block:", error);
//          }
//      }
//  }

//  DynamicDashboard.template = "owl.dynamic_dashboard";
//  DynamicDashboard.components = { DynamicDashboardTile, DynamicDashboardChart };

//  registry.category("actions").add("owl.dynamic_dashboard", DynamicDashboard);
