odoo.define('pos', require => {
    "use strict";

    const models = require('point_of_sale.models');

    const session = require('web.session');
    const rpc = require('web.rpc');
    
    const given_school_codes = new RegExp('[\?&]school_code_ids=([^&#]*)').exec(window.location.href);
    session.user_context.allowed_school_code_ids = given_school_codes 
        && given_school_codes[1] 
        && given_school_codes[1].split(',').map(r => parseInt(r)) || false;
//     const Session = require('web.Session');

//     const AbstractWebClient = require('web.WebClient')
//     const utils = require('web.utils');
//     const dom = require('web.dom');

    const _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        
        // :'( Hard Inheritance'
        load_new_partners: function() {
            var self = this;
            return new Promise(function (resolve, reject) {
                var fields = _.find(self.models, function(model){ return model.label === 'load_partners'; }).fields;
                var domain = self.prepare_new_partners_domain();
                rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                    context: session.user_context,
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function (partners) {
                    if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
                        resolve();
                    } else {
                        reject();
                    }
                }, function (type, err) { reject(); });
            });
        }
    });
});