/*! For license information please see 323.508c63790aeddf02.js.LICENSE.txt */
export const __webpack_ids__=["323"];export const __webpack_modules__={75972:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{u:()=>r});var o=i(57900),s=i(28105),n=e([o]);o=(n.then?(await n)():n)[0];const r=(e,t)=>{try{return l(t)?.of(e)??e}catch{return e}},l=(0,s.Z)((e=>new Intl.DisplayNames(e.language,{type:"language",fallback:"code"})));a()}catch(r){a(r)}}))},89395:function(e,t,i){i.d(t,{J:()=>o,_:()=>s});const a=/{%|{{/,o=e=>a.test(e),s=e=>{if(!e)return!1;if("string"==typeof e)return o(e);if("object"==typeof e){return(Array.isArray(e)?e:Object.values(e)).some((e=>e&&s(e)))}return!1}},69187:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(73742),o=i(59048),s=i(7616),n=i(29740),r=i(41806),l=i(75972),c=i(32518),d=(i(93795),i(29490),e([l]));l=(d.then?(await d)():d)[0];const h="preferred",p="last_used";class u extends o.oi{get _default(){return this.includeLastUsed?p:h}render(){if(!this._pipelines)return o.Ld;const e=this.value??this._default;return o.dy`
      <ha-select
        .label=${this.label||this.hass.localize("ui.components.pipeline-picker.pipeline")}
        .value=${e}
        .required=${this.required}
        .disabled=${this.disabled}
        @selected=${this._changed}
        @closed=${r.U}
        fixedMenuPosition
        naturalMenuWidth
      >
        ${this.includeLastUsed?o.dy`
              <ha-list-item .value=${p}>
                ${this.hass.localize("ui.components.pipeline-picker.last_used")}
              </ha-list-item>
            `:null}
        <ha-list-item .value=${h}>
          ${this.hass.localize("ui.components.pipeline-picker.preferred",{preferred:this._pipelines.find((e=>e.id===this._preferredPipeline))?.name})}
        </ha-list-item>
        ${this._pipelines.map((e=>o.dy`<ha-list-item .value=${e.id}>
              ${e.name}
              (${(0,l.u)(e.language,this.hass.locale)})
            </ha-list-item>`))}
      </ha-select>
    `}firstUpdated(e){super.firstUpdated(e),(0,c.SC)(this.hass).then((e=>{this._pipelines=e.pipelines,this._preferredPipeline=e.preferred_pipeline}))}_changed(e){const t=e.target;!this.hass||""===t.value||t.value===this.value||void 0===this.value&&t.value===this._default||(this.value=t.value===this._default?void 0:t.value,(0,n.B)(this,"value-changed",{value:this.value}))}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.includeLastUsed=!1,this._preferredPipeline=null}}u.styles=o.iv`
    ha-select {
      width: 100%;
    }
  `,(0,a.__decorate)([(0,s.Cb)()],u.prototype,"value",void 0),(0,a.__decorate)([(0,s.Cb)()],u.prototype,"label",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],u.prototype,"hass",void 0),(0,a.__decorate)([(0,s.Cb)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.Cb)({type:Boolean})],u.prototype,"required",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],u.prototype,"includeLastUsed",void 0),(0,a.__decorate)([(0,s.SB)()],u.prototype,"_pipelines",void 0),(0,a.__decorate)([(0,s.SB)()],u.prototype,"_preferredPipeline",void 0),u=(0,a.__decorate)([(0,s.Mo)("ha-assist-pipeline-picker")],u),t()}catch(h){t(h)}}))},57027:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(73742),o=i(59048),s=i(7616),n=(i(40830),i(27341)),r=e([n]);n=(r.then?(await r)():r)[0];const l="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";class c extends o.oi{render(){return o.dy`
      <ha-tooltip .placement=${this.position} .content=${this.label}>
        <ha-svg-icon .path=${l}></ha-svg-icon>
      </ha-tooltip>
    `}constructor(...e){super(...e),this.position="top"}}c.styles=o.iv`
    ha-svg-icon {
      --mdc-icon-size: var(--ha-help-tooltip-size, 14px);
      color: var(--ha-help-tooltip-color, var(--disabled-text-color));
    }
  `,(0,a.__decorate)([(0,s.Cb)()],c.prototype,"label",void 0),(0,a.__decorate)([(0,s.Cb)()],c.prototype,"position",void 0),c=(0,a.__decorate)([(0,s.Mo)("ha-help-tooltip")],c),t()}catch(l){t(l)}}))},91391:function(e,t,i){var a=i(73742),o=i(59048),s=i(7616),n=i(29740);const r=e=>e.replace(/^_*(.)|_+(.)/g,((e,t,i)=>t?t.toUpperCase():" "+i.toUpperCase()));i(90256),i(57264),i(3847);const l=[],c=e=>o.dy`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${e.icon} slot="start"></ha-icon>
    <span slot="headline">${e.title||e.path}</span>
    ${e.title?o.dy`<span slot="supporting-text">${e.path}</span>`:o.Ld}
  </ha-combo-box-item>
`,d=(e,t,i)=>({path:`/${e}/${t.path??i}`,icon:t.icon??"mdi:view-compact",title:t.title??(t.path?r(t.path):`${i}`)}),h=(e,t)=>({path:`/${t.url_path}`,icon:t.icon??"mdi:view-dashboard",title:t.url_path===e.defaultPanel?e.localize("panel.states"):e.localize(`panel.${t.title}`)||t.title||(t.url_path?r(t.url_path):"")});class p extends o.oi{render(){return o.dy`
      <ha-combo-box
        .hass=${this.hass}
        item-value-path="path"
        item-label-path="path"
        .value=${this._value}
        allow-custom-value
        .filteredItems=${this.navigationItems}
        .label=${this.label}
        .helper=${this.helper}
        .disabled=${this.disabled}
        .required=${this.required}
        .renderer=${c}
        @opened-changed=${this._openedChanged}
        @value-changed=${this._valueChanged}
        @filter-changed=${this._filterChanged}
      >
      </ha-combo-box>
    `}async _openedChanged(e){this._opened=e.detail.value,this._opened&&!this.navigationItemsLoaded&&this._loadNavigationItems()}async _loadNavigationItems(){this.navigationItemsLoaded=!0;const e=Object.entries(this.hass.panels).map((([e,t])=>({id:e,...t}))),t=e.filter((e=>"lovelace"===e.component_name)),i=await Promise.all(t.map((e=>{return(t=this.hass.connection,i="lovelace"===e.url_path?null:e.url_path,a=!0,t.sendMessagePromise({type:"lovelace/config",url_path:i,force:a})).then((t=>[e.id,t])).catch((t=>[e.id,void 0]));var t,i,a}))),a=new Map(i);this.navigationItems=[];for(const o of e){this.navigationItems.push(h(this.hass,o));const e=a.get(o.id);e&&"views"in e&&e.views.forEach(((e,t)=>this.navigationItems.push(d(o.url_path,e,t))))}this.comboBox.filteredItems=this.navigationItems}shouldUpdate(e){return!this._opened||e.has("_opened")}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,n.B)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}_filterChanged(e){const t=e.detail.value.toLowerCase();if(t.length>=2){const e=[];this.navigationItems.forEach((i=>{(i.path.toLowerCase().includes(t)||i.title.toLowerCase().includes(t))&&e.push(i)})),e.length>0?this.comboBox.filteredItems=e:this.comboBox.filteredItems=[]}else this.comboBox.filteredItems=this.navigationItems}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this._opened=!1,this.navigationItemsLoaded=!1,this.navigationItems=l}}p.styles=o.iv`
    ha-icon,
    ha-svg-icon {
      color: var(--primary-text-color);
      position: relative;
      bottom: 0px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `,(0,a.__decorate)([(0,s.Cb)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,s.Cb)()],p.prototype,"label",void 0),(0,a.__decorate)([(0,s.Cb)()],p.prototype,"value",void 0),(0,a.__decorate)([(0,s.Cb)()],p.prototype,"helper",void 0),(0,a.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.Cb)({type:Boolean})],p.prototype,"required",void 0),(0,a.__decorate)([(0,s.SB)()],p.prototype,"_opened",void 0),(0,a.__decorate)([(0,s.IO)("ha-combo-box",!0)],p.prototype,"comboBox",void 0),p=(0,a.__decorate)([(0,s.Mo)("ha-navigation-picker")],p)},53179:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaSelectorUiAction:()=>d});var o=i(73742),s=i(59048),n=i(7616),r=i(29740),l=i(18234),c=e([l]);l=(c.then?(await c)():c)[0];class d extends s.oi{render(){return s.dy`
      <hui-action-editor
        .label=${this.label}
        .hass=${this.hass}
        .config=${this.value}
        .actions=${this.selector.ui_action?.actions}
        .defaultAction=${this.selector.ui_action?.default_action}
        .tooltipText=${this.helper}
        @value-changed=${this._valueChanged}
      ></hui-action-editor>
    `}_valueChanged(e){e.stopPropagation(),(0,r.B)(this,"value-changed",{value:e.detail.value})}}(0,o.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"selector",void 0),(0,o.__decorate)([(0,n.Cb)({attribute:!1})],d.prototype,"value",void 0),(0,o.__decorate)([(0,n.Cb)()],d.prototype,"label",void 0),(0,o.__decorate)([(0,n.Cb)()],d.prototype,"helper",void 0),d=(0,o.__decorate)([(0,n.Mo)("ha-selector-ui_action")],d),a()}catch(d){a(d)}}))},32518:function(e,t,i){i.d(t,{Dy:()=>c,PA:()=>n,SC:()=>s,Xp:()=>o,af:()=>l,eP:()=>a,jZ:()=>r});const a=(e,t,i)=>"run-start"===t.type?e={init_options:i,stage:"ready",run:t.data,events:[t]}:e?((e="wake_word-start"===t.type?{...e,stage:"wake_word",wake_word:{...t.data,done:!1}}:"wake_word-end"===t.type?{...e,wake_word:{...e.wake_word,...t.data,done:!0}}:"stt-start"===t.type?{...e,stage:"stt",stt:{...t.data,done:!1}}:"stt-end"===t.type?{...e,stt:{...e.stt,...t.data,done:!0}}:"intent-start"===t.type?{...e,stage:"intent",intent:{...t.data,done:!1}}:"intent-end"===t.type?{...e,intent:{...e.intent,...t.data,done:!0}}:"tts-start"===t.type?{...e,stage:"tts",tts:{...t.data,done:!1}}:"tts-end"===t.type?{...e,tts:{...e.tts,...t.data,done:!0}}:"run-end"===t.type?{...e,stage:"done"}:"error"===t.type?{...e,stage:"error",error:t.data}:{...e}).events=[...e.events,t],e):void console.warn("Received unexpected event before receiving session",t),o=(e,t,i)=>e.connection.subscribeMessage(t,{...i,type:"assist_pipeline/run"}),s=e=>e.callWS({type:"assist_pipeline/pipeline/list"}),n=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:t}),r=(e,t)=>e.callWS({type:"assist_pipeline/pipeline/create",...t}),l=(e,t,i)=>e.callWS({type:"assist_pipeline/pipeline/update",pipeline_id:t,...i}),c=e=>e.callWS({type:"assist_pipeline/language/list"})},47469:function(e,t,i){i.d(t,{F3:()=>o,Lh:()=>a,t4:()=>s});const a=(e,t,i)=>e(`component.${t}.title`)||i?.name||t,o=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},s=(e,t)=>e.callWS({type:"manifest/get",integration:t})},18234:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(73742),o=i(59048),s=i(7616),n=i(28105),r=i(29740),l=i(41806),c=i(69187),d=i(57027),h=(i(93795),i(91391),i(45618)),p=e([c,d,h]);[c,d,h]=p.then?(await p)():p;const u=["more-info","toggle","navigate","url","perform-action","assist","none"],_=[{name:"navigation_path",selector:{navigation:{}}}],v=[{type:"grid",name:"",schema:[{name:"pipeline_id",selector:{assist_pipeline:{include_last_used:!0}}},{name:"start_listening",selector:{boolean:{}}}]}];class g extends o.oi{get _navigation_path(){const e=this.config;return e?.navigation_path||""}get _url_path(){const e=this.config;return e?.url_path||""}get _service(){const e=this.config;return e?.perform_action||e?.service||""}updated(e){super.updated(e),e.has("defaultAction")&&e.get("defaultAction")!==this.defaultAction&&this._select.layoutOptions()}render(){if(!this.hass)return o.Ld;const e=this.actions??u;let t=this.config?.action||"default";return"call-service"===t&&(t="perform-action"),o.dy`
      <div class="dropdown">
        <ha-select
          .label=${this.label}
          .configValue=${"action"}
          @selected=${this._actionPicked}
          .value=${t}
          @closed=${l.U}
          fixedMenuPosition
          naturalMenuWidth
        >
          <ha-list-item value="default">
            ${this.hass.localize("ui.panel.lovelace.editor.action-editor.actions.default_action")}
            ${this.defaultAction?` (${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${this.defaultAction}`).toLowerCase()})`:o.Ld}
          </ha-list-item>
          ${e.map((e=>o.dy`
              <ha-list-item .value=${e}>
                ${this.hass.localize(`ui.panel.lovelace.editor.action-editor.actions.${e}`)}
              </ha-list-item>
            `))}
        </ha-select>
        ${this.tooltipText?o.dy`
              <ha-help-tooltip .label=${this.tooltipText}></ha-help-tooltip>
            `:o.Ld}
      </div>
      ${"navigate"===this.config?.action?o.dy`
            <ha-form
              .hass=${this.hass}
              .schema=${_}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:o.Ld}
      ${"url"===this.config?.action?o.dy`
            <ha-textfield
              .label=${this.hass.localize("ui.panel.lovelace.editor.action-editor.url_path")}
              .value=${this._url_path}
              .configValue=${"url_path"}
              @input=${this._valueChanged}
            ></ha-textfield>
          `:o.Ld}
      ${"call-service"===this.config?.action||"perform-action"===this.config?.action?o.dy`
            <ha-service-control
              .hass=${this.hass}
              .value=${this._serviceAction(this.config)}
              .showAdvanced=${this.hass.userData?.showAdvanced}
              narrow
              @value-changed=${this._serviceValueChanged}
            ></ha-service-control>
          `:o.Ld}
      ${"assist"===this.config?.action?o.dy`
            <ha-form
              .hass=${this.hass}
              .schema=${v}
              .data=${this.config}
              .computeLabel=${this._computeFormLabel}
              @value-changed=${this._formValueChanged}
            >
            </ha-form>
          `:o.Ld}
    `}_actionPicked(e){if(e.stopPropagation(),!this.hass)return;let t=this.config?.action;"call-service"===t&&(t="perform-action");const i=e.target.value;if(t===i)return;if("default"===i)return void(0,r.B)(this,"value-changed",{value:void 0});let a;switch(i){case"url":a={url_path:this._url_path};break;case"perform-action":a={perform_action:this._service};break;case"navigate":a={navigation_path:this._navigation_path}}(0,r.B)(this,"value-changed",{value:{action:i,...a}})}_valueChanged(e){if(e.stopPropagation(),!this.hass)return;const t=e.target,i=e.target.value??e.target.checked;this[`_${t.configValue}`]!==i&&t.configValue&&(0,r.B)(this,"value-changed",{value:{...this.config,[t.configValue]:i}})}_formValueChanged(e){e.stopPropagation();const t=e.detail.value;(0,r.B)(this,"value-changed",{value:t})}_computeFormLabel(e){return this.hass?.localize(`ui.panel.lovelace.editor.action-editor.${e.name}`)}_serviceValueChanged(e){e.stopPropagation();const t={...this.config,action:"perform-action",perform_action:e.detail.value.action||"",data:e.detail.value.data,target:e.detail.value.target||{}};e.detail.value.data||delete t.data,"service_data"in t&&delete t.service_data,"service"in t&&delete t.service,(0,r.B)(this,"value-changed",{value:t})}constructor(...e){super(...e),this._serviceAction=(0,n.Z)((e=>({action:this._service,...e.data||e.service_data?{data:e.data??e.service_data}:null,target:e.target})))}}g.styles=o.iv`
    .dropdown {
      position: relative;
    }
    ha-help-tooltip {
      position: absolute;
      right: 40px;
      top: 16px;
      inset-inline-start: initial;
      inset-inline-end: 40px;
      direction: var(--direction);
    }
    ha-select,
    ha-textfield {
      width: 100%;
    }
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      display: block;
    }
    ha-textfield,
    ha-service-control,
    ha-navigation-picker,
    ha-form {
      margin-top: 8px;
    }
    ha-service-control {
      --service-control-padding: 0;
    }
  `,(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"config",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"label",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"actions",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"defaultAction",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"tooltipText",void 0),(0,a.__decorate)([(0,s.Cb)({attribute:!1})],g.prototype,"hass",void 0),(0,a.__decorate)([(0,s.IO)("ha-select")],g.prototype,"_select",void 0),g=(0,a.__decorate)([(0,s.Mo)("hui-action-editor")],g),t()}catch(u){t(u)}}))},15606:function(e,t,i){i.d(t,{C:()=>o});var a=i(29740);const o=(e,t)=>(0,a.B)(e,"hass-notification",t)},12790:function(e,t,i){i.d(t,{C:()=>p});var a=i(35340),o=i(5277),s=i(93847);class n{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class r{get(){return this.Y}pause(){this.Y??=new Promise((e=>this.Z=e))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var l=i(83522);const c=e=>!(0,o.pt)(e)&&"function"==typeof e.then,d=1073741823;class h extends s.sR{render(...e){return e.find((e=>!c(e)))??a.Jb}update(e,t){const i=this._$Cbt;let o=i.length;this._$Cbt=t;const s=this._$CK,n=this._$CX;this.isConnected||this.disconnected();for(let a=0;a<t.length&&!(a>this._$Cwt);a++){const e=t[a];if(!c(e))return this._$Cwt=a,e;a<o&&e===i[a]||(this._$Cwt=d,o=0,Promise.resolve(e).then((async t=>{for(;n.get();)await n.get();const i=s.deref();if(void 0!==i){const a=i._$Cbt.indexOf(e);a>-1&&a<i._$Cwt&&(i._$Cwt=a,i.setValue(t))}})))}return a.Jb}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=d,this._$Cbt=[],this._$CK=new n(this),this._$CX=new r}}const p=(0,l.XM)(h)}};
//# sourceMappingURL=323.508c63790aeddf02.js.map