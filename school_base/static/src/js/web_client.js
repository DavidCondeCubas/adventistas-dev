odoo.define('school_base.session.inherit', require => {
    "use strict";

    const session = require('web.session');
    const Session = require('web.Session');
    
    const AbstractWebClient = require('web.WebClient')
    const utils = require('web.utils');
    const dom = require('web.dom');

    AbstractWebClient.include({
        /* This returns a promise */
        start() {
            const res = this._super(...arguments);

            const state = $.bbq.getState();

            // District codes
            const current_district_code_id = session.user_district_codes.current_district_code.id;
            if (!state.districtCodeIds) {
                state.districtCodeIds = utils.get_cookie('districtCodeIds') !== null ? utils.get_cookie('districtCodeIds') : String(current_district_code_id);
            }

            let stateDistrictCodeIDS = _.map(state.districtCodeIds.split(','), cid => parseInt(cid));
            const userDistrictCodeIDS = _.map(session.user_district_codes.allowed_district_codes, dc => dc.id);
            // Check that the user has access to all the companies
            if (!_.isEmpty(_.difference(stateDistrictCodeIDS, userDistrictCodeIDS))) {
                state.districtCodeIds = String(current_district_code_id);
                stateDistrictCodeIDS = [current_district_code_id]
            }


            // School codes
            const current_school_code_id = session.user_school_codes.current_school_code.id;
            if (!state.schoolCodeIds) {
                state.schoolCodeIds = utils.get_cookie('schoolCodeIds') !== null ? utils.get_cookie('schoolCodeIds') : String(current_school_code_id);
            }

            let stateSchoolCodeIDS = _.map(state.schoolCodeIds.split(','), cid => parseInt(cid));
            const userSchoolCodeIDS = _.map(session.user_school_codes.allowed_school_codes, dc => dc.id);
            // Check that the user has access to all the companies
            if (!_.isEmpty(_.difference(stateSchoolCodeIDS, userSchoolCodeIDS))) {
                state.schoolCodeIds = String(current_school_code_id);
                stateSchoolCodeIDS = [current_school_code_id]
            }
            session.user_context.allowed_district_code_ids = stateDistrictCodeIDS;
            session.user_context.allowed_school_code_ids = stateSchoolCodeIDS;

            $.bbq.pushState({
                "districtCodeIds": String(stateDistrictCodeIDS),
                "schoolCodeIds": String(stateSchoolCodeIDS),
            });
            
            return res;
        },

        _onPushState(e) {
            e.data.state.districtCodeIds = $.bbq.getState().districtCodeIds;
            e.data.state.schoolCodeIds = $.bbq.getState().schoolCodeIds;
            this._super(...arguments);
        },

        /**
         * HARD Override
         * @Override
         * @param display
         */
        toggle_home_menu(display) {
            if (display === this.home_menu_displayed) {
                return; // nothing to do (prevents erasing previously detached webclient content)
            }
            if (display) {
                this.clear_uncommitted_changes().then(() => {
                    // Save the current scroll position
                    this.scrollPosition = this.getScrollPosition();

                    // Detach the web_client contents
                    const $to_detach = this.$el.contents()
                            .not(this.menu.$el)
                            .not('.o_loading')
                            .not('.o_in_home_menu')
                            .not('.o_notification_manager');
                    this.web_client_content = document.createDocumentFragment();
                    dom.detach([{widget: this.action_manager}], {$to_detach: $to_detach}).appendTo(this.web_client_content);

                    // Attach the home_menu
                    this.append_home_menu();
                    this.$el.addClass('o_home_menu_background');

                    // Save and clear the url
                    this.url = $.bbq.getState();
                    if (location.hash) {
                        this._ignore_hashchange = true;
                        $.bbq.pushState('#home', 2); // merge_mode 2 to replace the current state
                    }
                    $.bbq.pushState({
                        'cids': this.url.cids,
                        'districtCodeIds': this.url.districtCodeIds,
                        'schoolCodeIds': this.url.schoolCodeIds,
                    }, 0);

                    this.menu.toggle_mode(true, this.action_manager.getCurrentAction() !== null);
                });
            } else {
                dom.detach([{widget: this.home_menu}]);
                dom.append(this.$el, [this.web_client_content], {
                    in_DOM: true,
                    callbacks: [{widget: this.action_manager}],
                });
                this.trigger_up('scrollTo', this.scrollPosition);
                this.home_menu_displayed = false;
                this.$el.removeClass('o_home_menu_background');
                this.menu.toggle_mode(false, this.action_manager.getCurrentAction() !== null);
            }
        },
    })

    Session.include({
        setSchoolCodes: function (main_district_code_id, district_code_ids,
                                  main_school_code_id, school_code_ids) {
            var hash = $.bbq.getState()
            hash.districtCodeIds = district_code_ids.sort(function(a, b) {
                if (a === main_district_code_id) {
                    return -1;
                } else if (b === main_district_code_id) {
                    return 1;
                } else {
                    return a - b;
                }
            }).join(',');

            hash.schoolCodeIds = school_code_ids.sort(function(a, b) {
                if (a === main_school_code_id) {
                    return -1;
                } else if (b === main_school_code_id) {
                    return 1;
                } else {
                    return a - b;
                }
            }).join(',');

            utils.set_cookie('districtCodeIds', hash.districtCodeIds || String(main_district_code_id));
            utils.set_cookie('schoolCodeIds', hash.schoolCodeIds || String(main_school_code_id));

            $.bbq.pushState({
                'districtCodeIds': hash.districtCodeIds,
                'schoolCodeIds': hash.schoolCodeIds,
            }, 0);
            location.reload();
        },
    })
    
})