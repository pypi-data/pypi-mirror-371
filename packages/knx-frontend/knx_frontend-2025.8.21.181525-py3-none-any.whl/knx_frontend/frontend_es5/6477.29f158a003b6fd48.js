"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6477"],{85163:function(e,t,i){i.d(t,{wZ:function(){return a},jL:function(){return o}});i(26847),i(81738),i(94814),i(6989),i(20655),i(27530);var s=i(28105),r=i(31298);i(67886),i(65451),i(46015),i(38334),i(94880),i(75643),i(29761);const o=e=>{var t;return null===(t=e.name_by_user||e.name)||void 0===t?void 0:t.trim()},a=(e,t,i)=>o(e)||i&&n(t,i)||t.localize("ui.panel.config.devices.unnamed_device",{type:t.localize(`ui.panel.config.devices.type.${e.entry_type||"device"}`)}),n=(e,t)=>{for(const i of t||[]){const t="string"==typeof i?i:i.entity_id,s=e.states[t];if(s)return(0,r.C)(s)}};(0,s.Z)((e=>function(e){const t=new Set,i=new Set;for(const s of e)i.has(s)?t.add(s):i.add(s);return t}(Object.values(e).map((e=>o(e))).filter((e=>void 0!==e)))))},39379:function(e,t,i){i.d(t,{v:function(){return s}});const s=(e,t)=>{const i=e.area_id,s=i?t.areas[i]:void 0,r=null==s?void 0:s.floor_id;return{device:e,area:s||null,floor:(r?t.floors[r]:void 0)||null}}},86605:function(e,t,i){i.a(e,(async function(e,t){try{i(39710),i(26847),i(81738),i(33480),i(94814),i(6989),i(72489),i(18514),i(1455),i(56389),i(27530);var s=i(73742),r=i(59048),o=i(7616),a=i(28105),n=i(29740),d=i(71188),c=i(85163),l=i(76151),u=i(39379),h=i(51068),v=i(57774),p=i(47469),_=i(37198),y=i(33321),b=e([y]);y=(b.then?(await b)():b)[0];let m,f,g,$,C,D,k,L,x=e=>e;class F extends r.oi{firstUpdated(e){super.firstUpdated(e),this._loadConfigEntries()}async _loadConfigEntries(){const e=await(0,h.pB)(this.hass);this._configEntryLookup=Object.fromEntries(e.map((e=>[e.entry_id,e])))}render(){var e;const t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.device-picker.placeholder"),i=this.hass.localize("ui.components.device-picker.no_match"),s=this._valueRenderer(this._configEntryLookup);return(0,r.dy)(m||(m=x`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .hideClearIcon=${0}
        .valueRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.searchLabel,i,t,this.value,this._rowRenderer,this._getItems,this.hideClearIcon,s,this._valueChanged)}async open(){var e;await this.updateComplete,await(null===(e=this._picker)||void 0===e?void 0:e.open())}_valueChanged(e){e.stopPropagation();const t=e.detail.value;this.value=t,(0,n.B)(this,"value-changed",{value:t})}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this._configEntryLookup={},this._getItems=()=>this._getDevices(this.hass.devices,this.hass.entities,this._configEntryLookup,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeDevices),this._getDevices=(0,a.Z)(((e,t,i,s,r,o,a,n,h)=>{const _=Object.values(e),y=Object.values(t);let b={};(s||r||o||n)&&(b=(0,v.R6)(y));let m=_.filter((e=>e.id===this.value||!e.disabled_by));s&&(m=m.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>s.includes((0,l.M)(e.entity_id))))}))),r&&(m=m.filter((e=>{const t=b[e.id];return!t||!t.length||y.every((e=>!r.includes((0,l.M)(e.entity_id))))}))),h&&(m=m.filter((e=>!h.includes(e.id)))),o&&(m=m.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&b[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&o.includes(t.attributes.device_class))}))}))),n&&(m=m.filter((e=>{const t=b[e.id];return!(!t||!t.length)&&t.some((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))}))),a&&(m=m.filter((e=>e.id===this.value||a(e))));return m.map((e=>{const t=(0,c.wZ)(e,this.hass,b[e.id]),{area:s}=(0,u.v)(e,this.hass),r=s?(0,d.D)(s):void 0,o=e.primary_config_entry?null==i?void 0:i[e.primary_config_entry]:void 0,a=null==o?void 0:o.domain,n=a?(0,p.Lh)(this.hass.localize,a):void 0;return{id:e.id,label:"",primary:t||this.hass.localize("ui.components.device-picker.unnamed_device"),secondary:r,domain:null==o?void 0:o.domain,domain_name:n,search_labels:[t,r,a,n].filter(Boolean),sorting_label:t||"zzz"}}))})),this._valueRenderer=(0,a.Z)((e=>t=>{var i;const s=t,o=this.hass.devices[s];if(!o)return(0,r.dy)(f||(f=x`<span slot="headline">${0}</span>`),s);const{area:a}=(0,u.v)(o,this.hass),n=o?(0,c.jL)(o):void 0,l=a?(0,d.D)(a):void 0,h=o.primary_config_entry?e[o.primary_config_entry]:void 0;return(0,r.dy)(g||(g=x`
        ${0}
        <span slot="headline">${0}</span>
        <span slot="supporting-text">${0}</span>
      `),h?(0,r.dy)($||($=x`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />`),(0,_.X1)({domain:h.domain,type:"icon",darkOptimized:null===(i=this.hass.themes)||void 0===i?void 0:i.darkMode})):r.Ld,n,l)})),this._rowRenderer=e=>(0,r.dy)(C||(C=x`
    <ha-combo-box-item type="button">
      ${0}

      <span slot="headline">${0}</span>
      ${0}
      ${0}
    </ha-combo-box-item>
  `),e.domain?(0,r.dy)(D||(D=x`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />
          `),(0,_.X1)({domain:e.domain,type:"icon",darkOptimized:this.hass.themes.darkMode})):r.Ld,e.primary,e.secondary?(0,r.dy)(k||(k=x`<span slot="supporting-text">${0}</span>`),e.secondary):r.Ld,e.domain_name?(0,r.dy)(L||(L=x`
            <div slot="trailing-supporting-text" class="domain">
              ${0}
            </div>
          `),e.domain_name):r.Ld)}}(0,s.__decorate)([(0,o.Cb)({attribute:!1})],F.prototype,"hass",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],F.prototype,"autofocus",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],F.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],F.prototype,"required",void 0),(0,s.__decorate)([(0,o.Cb)()],F.prototype,"label",void 0),(0,s.__decorate)([(0,o.Cb)()],F.prototype,"value",void 0),(0,s.__decorate)([(0,o.Cb)()],F.prototype,"helper",void 0),(0,s.__decorate)([(0,o.Cb)()],F.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.Cb)({type:String,attribute:"search-label"})],F.prototype,"searchLabel",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1,type:Array})],F.prototype,"createDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-domains"})],F.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-domains"})],F.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-device-classes"})],F.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-devices"})],F.prototype,"excludeDevices",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],F.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],F.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:"hide-clear-icon",type:Boolean})],F.prototype,"hideClearIcon",void 0),(0,s.__decorate)([(0,o.IO)("ha-generic-picker")],F.prototype,"_picker",void 0),(0,s.__decorate)([(0,o.SB)()],F.prototype,"_configEntryLookup",void 0),F=(0,s.__decorate)([(0,o.Mo)("ha-device-picker")],F),t()}catch(m){t(m)}}))},16464:function(e,t,i){i.a(e,(async function(e,t){try{i(39710),i(26847),i(81738),i(94814),i(6989),i(1455),i(56389),i(27530);var s=i(73742),r=i(59048),o=i(7616),a=i(29740),n=i(86605),d=e([n]);n=(d.then?(await d)():d)[0];let c,l,u,h=e=>e;class v extends r.oi{render(){if(!this.hass)return r.Ld;const e=this._currentDevices;return(0,r.dy)(c||(c=h`
      ${0}
      <div>
        <ha-device-picker
          allow-custom-entity
          .hass=${0}
          .helper=${0}
          .deviceFilter=${0}
          .entityFilter=${0}
          .includeDomains=${0}
          .excludeDomains=${0}
          .excludeDevices=${0}
          .includeDeviceClasses=${0}
          .label=${0}
          .disabled=${0}
          .required=${0}
          @value-changed=${0}
        ></ha-device-picker>
      </div>
    `),e.map((e=>(0,r.dy)(l||(l=h`
          <div>
            <ha-device-picker
              allow-custom-entity
              .curValue=${0}
              .hass=${0}
              .deviceFilter=${0}
              .entityFilter=${0}
              .includeDomains=${0}
              .excludeDomains=${0}
              .includeDeviceClasses=${0}
              .value=${0}
              .label=${0}
              .disabled=${0}
              @value-changed=${0}
            ></ha-device-picker>
          </div>
        `),e,this.hass,this.deviceFilter,this.entityFilter,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,e,this.pickedDeviceLabel,this.disabled,this._deviceChanged))),this.hass,this.helper,this.deviceFilter,this.entityFilter,this.includeDomains,this.excludeDomains,e,this.includeDeviceClasses,this.pickDeviceLabel,this.disabled,this.required&&!e.length,this._addDevice)}get _currentDevices(){return this.value||[]}async _updateDevices(e){(0,a.B)(this,"value-changed",{value:e}),this.value=e}_deviceChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;i!==t&&(void 0===i?this._updateDevices(this._currentDevices.filter((e=>e!==t))):this._updateDevices(this._currentDevices.map((e=>e===t?i:e))))}async _addDevice(e){e.stopPropagation();const t=e.detail.value;if(e.currentTarget.value="",!t)return;const i=this._currentDevices;i.includes(t)||this._updateDevices([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1}}v.styles=(0,r.iv)(u||(u=h`
    div {
      margin-top: 8px;
    }
  `)),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],v.prototype,"hass",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array})],v.prototype,"value",void 0),(0,s.__decorate)([(0,o.Cb)()],v.prototype,"helper",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],v.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.Cb)({type:Boolean})],v.prototype,"required",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-domains"})],v.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"exclude-domains"})],v.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.Cb)({type:Array,attribute:"include-device-classes"})],v.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:"picked-device-label"})],v.prototype,"pickedDeviceLabel",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:"pick-device-label"})],v.prototype,"pickDeviceLabel",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],v.prototype,"deviceFilter",void 0),(0,s.__decorate)([(0,o.Cb)({attribute:!1})],v.prototype,"entityFilter",void 0),v=(0,s.__decorate)([(0,o.Mo)("ha-devices-picker")],v),t()}catch(c){t(c)}}))},12840:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaDeviceSelector:function(){return $}});i(26847),i(81738),i(94814),i(72489),i(27530);var r=i(73742),o=i(59048),a=i(7616),n=i(28105),d=i(74608),c=i(29740),l=i(57774),u=i(71170),h=i(51068),v=i(45103),p=i(86605),_=i(16464),y=e([p,_]);[p,_]=y.then?(await y)():y;let b,m,f,g=e=>e;class $ extends o.oi{_hasIntegration(e){var t,i;return(null===(t=e.device)||void 0===t?void 0:t.filter)&&(0,d.r)(e.device.filter).some((e=>e.integration))||(null===(i=e.device)||void 0===i?void 0:i.entity)&&(0,d.r)(e.device.entity).some((e=>e.integration))}willUpdate(e){var t,i;e.get("selector")&&void 0!==this.value&&(null!==(t=this.selector.device)&&void 0!==t&&t.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,c.B)(this,"value-changed",{value:this.value})):null!==(i=this.selector.device)&&void 0!==i&&i.multiple||!Array.isArray(this.value)||(this.value=this.value[0],(0,c.B)(this,"value-changed",{value:this.value})))}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,u.m)(this.hass).then((e=>{this._entitySources=e})),!this._configEntries&&this._hasIntegration(this.selector)&&(this._configEntries=[],(0,h.pB)(this.hass).then((e=>{this._configEntries=e})))}render(){var e,t,i;return this._hasIntegration(this.selector)&&!this._entitySources?o.Ld:null!==(e=this.selector.device)&&void 0!==e&&e.multiple?(0,o.dy)(m||(m=g`
      ${0}
      <ha-devices-picker
        .hass=${0}
        .value=${0}
        .helper=${0}
        .deviceFilter=${0}
        .entityFilter=${0}
        .disabled=${0}
        .required=${0}
      ></ha-devices-picker>
    `),this.label?(0,o.dy)(f||(f=g`<label>${0}</label>`),this.label):"",this.hass,this.value,this.helper,this._filterDevices,null!==(t=this.selector.device)&&void 0!==t&&t.entity?this._filterEntities:void 0,this.disabled,this.required):(0,o.dy)(b||(b=g`
        <ha-device-picker
          .hass=${0}
          .value=${0}
          .label=${0}
          .helper=${0}
          .deviceFilter=${0}
          .entityFilter=${0}
          .disabled=${0}
          .required=${0}
          allow-custom-entity
        ></ha-device-picker>
      `),this.hass,this.value,this.label,this.helper,this._filterDevices,null!==(i=this.selector.device)&&void 0!==i&&i.entity?this._filterEntities:void 0,this.disabled,this.required)}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._deviceIntegrationLookup=(0,n.Z)(l.HP),this._filterDevices=e=>{var t;if(null===(t=this.selector.device)||void 0===t||!t.filter)return!0;const i=this._entitySources?this._deviceIntegrationLookup(this._entitySources,Object.values(this.hass.entities),Object.values(this.hass.devices),this._configEntries):void 0;return(0,d.r)(this.selector.device.filter).some((t=>(0,v.lE)(t,e,i)))},this._filterEntities=e=>(0,d.r)(this.selector.device.entity).some((t=>(0,v.lV)(t,e,this._entitySources)))}}(0,r.__decorate)([(0,a.Cb)({attribute:!1})],$.prototype,"hass",void 0),(0,r.__decorate)([(0,a.Cb)({attribute:!1})],$.prototype,"selector",void 0),(0,r.__decorate)([(0,a.SB)()],$.prototype,"_entitySources",void 0),(0,r.__decorate)([(0,a.SB)()],$.prototype,"_configEntries",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"value",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"label",void 0),(0,r.__decorate)([(0,a.Cb)()],$.prototype,"helper",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],$.prototype,"disabled",void 0),(0,r.__decorate)([(0,a.Cb)({type:Boolean})],$.prototype,"required",void 0),$=(0,r.__decorate)([(0,a.Mo)("ha-selector-device")],$),s()}catch(b){s(b)}}))},71170:function(e,t,i){i.d(t,{m:function(){return o}});i(26847),i(1455),i(27530);const s=async(e,t,i,r,o,...a)=>{const n=o,d=n[e],c=d=>r&&r(o,d.result)!==d.cacheKey?(n[e]=void 0,s(e,t,i,r,o,...a)):d.result;if(d)return d instanceof Promise?d.then(c):c(d);const l=i(o,...a);return n[e]=l,l.then((i=>{n[e]={result:i,cacheKey:null==r?void 0:r(o,i)},setTimeout((()=>{n[e]=void 0}),t)}),(()=>{n[e]=void 0})),l},r=e=>e.callWS({type:"entity/source"}),o=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},47469:function(e,t,i){i.d(t,{F3:function(){return r},Lh:function(){return s},t4:function(){return o}});i(16811);const s=(e,t,i)=>e(`component.${t}.title`)||(null==i?void 0:i.name)||t,r=(e,t)=>{const i={type:"manifest/list"};return t&&(i.integrations=t),e.callWS(i)},o=(e,t)=>e.callWS({type:"manifest/get",integration:t})},37198:function(e,t,i){i.d(t,{X1:function(){return s},u4:function(){return r},zC:function(){return o}});i(44261);const s=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,r=e=>e.split("/")[4],o=e=>e.startsWith("https://brands.home-assistant.io/")}}]);
//# sourceMappingURL=6477.29f158a003b6fd48.js.map