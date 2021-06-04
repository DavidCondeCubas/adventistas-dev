odoo.define('adm.backend.report.tracking.fields.view', require => {
    "use strict";

    console.log("ASDJSAKLDJHSAKÑLDJASKÑDJAKÑLDJSAKÑLDJÑAWEJ");

    const AbstractController = require('web.AbstractController');
    const AbstractModel = require('web.AbstractModel');
    const BasicRenderer = require('web.BasicRenderer');

    const qweb = require('web.qweb');
    const QWebView = qweb.View;
    const QWebRenderer = qweb.Renderer;
    const viewRegistry = require('web.view_registry');

    const AdmTrackingFieldsController = AbstractController.extend({});
    const AdmTrackingFieldsRenderer = QWebRenderer.extend({
        className: 'o_adm_tracking_fields_renderer',

        events: {
            'click .js_adm_collapse': '_toggleCollapse',
            'click .see_application': '_seeApplication',
        },

        init(parent, state, params) {
            this._super.apply(this, arguments);
        },

        _toggleCollapse({currentTarget}) {
            const targetQuery = currentTarget.dataset.target;
            const toggleTo = currentTarget.dataset.toggleTo;

            $(targetQuery).collapse(toggleTo);
        },

        _seeApplication(event) {
            const action = {
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                res_model: 'adm.application',
                res_id: parseInt(event.currentTarget.dataset.applicationId)
            }
            this.do_action(action);
        },


        // _render() {
        //     this.$el.append(
        //         $('<h1>').text('Hello World!')
        //     )
        //     return $.when();
        // }
    });
    const AdmTrackingFieldsModel = AbstractModel.extend({});

    // config: _.extend({}, QWebView.prototype.config, {
    //     Renderer: AdmTrackingFieldsRenderer,
    //     Controller: AdmTrackingFieldsController,
    // }),
    const AdmTrackingFieldsView = QWebView.extend({
        view_type: 'adm_tracking_fields',
        config: _.extend({}, QWebView.prototype.config, {
            Renderer: AdmTrackingFieldsRenderer,
        }),
    })

    viewRegistry.add('adm_tracking_fields', AdmTrackingFieldsView);

    return AdmTrackingFieldsView;

});