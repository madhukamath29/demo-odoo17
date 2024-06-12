//  /** @odoo-module */

 import { registry } from '@web/core/registry';
 const { Component, xml } = owl;

 export class DynamicDashboardTile extends Component {
     setup() {
         super.setup();
         this.getRecord = this.getRecord.bind(this);
         this.getConfiguration = this.getConfiguration.bind(this);
     }

     async getRecord() {
         try {
             const model_name = this.props.widget.model_name;
             if (model_name) {
                 await this.props.doAction({
                     type: 'ir.actions.act_window',
                     res_model: model_name,
                     view_mode: 'tree',
                     views: [[false, "tree"]],
                 });
             }
         } catch (error) {
             console.error("Error getting record:", error);
         }
     }

     async getConfiguration() {
         try {
             const id = this.props.widget.id;
             await this.props.doAction({
                 type: 'ir.actions.act_window',
                 res_model: 'dashboard.block',
                 res_id: id,
                 view_mode: 'form',
                 views: [[false, "form"]],
             });
         } catch (error) {
             console.error("Error getting configuration:", error);
         }
     }
 }

 DynamicDashboardTile.template = xml`
 <div class="col-sm-12 col-md-12 col-lg-3 tile block" t-att-data-id="this.props.widget.id">
     <div draggable="true" t-att-style="'background: ' + this.props.widget.tile_color" class="tile-container d-flex justify-content-around align-items-center position-relative w-100 h-auto my-3">
         <a t-on-click="getConfiguration" class="block_setting position-absolute tile-container__setting-icon cursor-pointer">
             <i class="fa fa-cog"></i>
         </a>
         <div t-on-click="getRecord" class="d-flex cursor-pointer">
             <div t-att-style="'color: ' + this.props.widget.icon_color" class="tile-container__icon-container bg-white d-flex justify-content-center align-items-center">
                 <i t-att-class="this.props.widget.icon" aria-hidden="true"></i>
             </div>
             <div class="tile-container__status-container" t-att-style="'color: ' + this.props.widget.text_color">
                 <h2 class="status-container__title" t-att-style="'color: ' + this.props.widget.text_color">
                     <t t-esc="this.props.widget.name"/>
                 </h2>
                 <div class="status-container__figures d-flex flex-wrap align-items-baseline">
                     <h3 class="mb-0 mb-md-1 mb-lg-0 mr-1" t-att-style="'color: ' + this.props.widget.text_color">
                         <t t-esc="this.props.widget.value"/>
                     </h3>
                 </div>
             </div>
         </div>
     </div>
 </div>`;

 DynamicDashboardTile.styles = `
 .tile-container {
     border-radius: 8px;
     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
     padding: 20px;
 }

 .tile-container__setting-icon {
     top: 10px;
     right: 10px;
 }

 .tile-container__icon-container {
     width: 60px;
     height: 60px;
     border-radius: 50%;
     margin-right: 15px;
 }

 .tile-container__status-container {
     display: flex;
     flex-direction: column;
 }

 .status-container__title {
     font-size: 1.2em;
     margin: 0;
 }

 .status-container__figures {
     font-size: 1.5em;
 }
 `;

//  registry.category("web_components").add("DynamicDashboardTile", DynamicDashboardTile);
