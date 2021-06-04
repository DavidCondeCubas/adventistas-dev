odoo.define('adm.application.invite', require => {
    "use strict";
    const core = require('web.core');
    const rpc = require('web.rpc');
    const session = require('web.session');

    document.addEventListener('DOMContentLoaded', () => {
        const invitationFormEl = document.getElementById('invitation_form');
        const newFamilyNameInputEl = document.getElementById('newFamilyName');
        const userPartnerId = parseInt(document.querySelector('meta[name="_user_partner_id"]').getAttribute('value'));
        const familySelectEl = document.getElementById('select_family');

        // Family Selection elements
        const familySelectModalEl = document.getElementById('family_select_modal');
        const $familySelectModalEl = $(familySelectModalEl);
        const familyUlList = document.querySelector('.o_adm_family_selection ul');
        const acceptFamilyModalButtonEl = document.querySelector('.js_accept_family_modal');

        // Modal new family elements
        const familyCreateModalEl = document.getElementById('family_select_modal_create');
        const $familyCreateModalEl = $(familyCreateModalEl);
        const saveNewFamilyButtonEl = document.querySelector('.js_save_new_family');

        // Form button
        const btnReject = document.getElementById('btn_reject_invitation');
        const btnAccept = document.getElementById('btn_accept_invitation');

        // Event handlers
        /**
         * @param {Event} event
         */
        function showFamilyModal(event) {
            event.preventDefault();
            this.blur();
            window.focus();
            $familySelectModalEl.modal({backdrop: 'static', keyboard: false});
        }

        async function submitNewFamily() {
            // Creating a new family for the students
            // const familyPartnerId = await session.rpc.query({

            const familyPartnerId = await $.ajax({
                url: '/admission/family/create',
                method: 'POST',
                data: {
                    csrf_token: core.csrf_token,
                    family_name: newFamilyNameInputEl.value
                }
            });

            // const familyPartnerId = await session.rpc(
            //     '/web/dataset/call_button', {
            //     model: 'res.partner',
            //     method: 'create',
            //     domain_id: null,
            //     context_id: args.length - 1,
            //     args: [{
            //         'name': newFamilyNameInputEl.value,
            //         'is_family': true,
            //         'is_company': true,
            //         'member_ids': [[4, userPartnerId, false]]
            //     }],
            //     kwargs: {}
            // });

            // await rpc.query({
            //     model: 'res.partner',
            //     method: 'write',
            //     args: [[userPartnerId], {
            //         'family_ids': [[4, familyPartnerId, false]]
            //     }],
            // });
            //
            const familyNewOption = document.createElement('OPTION');
            familyNewOption.value = familyPartnerId;
            familyNewOption.innerText = newFamilyNameInputEl.value;
            familySelectEl.appendChild(familyNewOption);

            const newFamilyLiEl = document.createElement('LI');

            newFamilyLiEl.innerHTML = `
                <li class="o_adm_family_select_item m-2 p-0" t-att-data-family-id="family_id.id">
                    <div class="p-2 d-flex justify-content-center">
                        <input type="radio" name="familyResponsibleCheckbox" value="${familyPartnerId}" />
                    </div>
                    <img src="/adm/static/img/contact_photo_placeholder.png" alt="avatar"/>
                    <p>${newFamilyNameInputEl.value}</p>
                </li>
                `;
            newFamilyLiEl.class = 'o_adm_family_select_item m-2 p-0';

            // The last child will be the + button
            // We need to prepend it
            familyUlList.insertBefore(newFamilyLiEl, familyUlList.lastElementChild);
            $familyCreateModalEl.modal('hide');
        }

        function submitFamilyModalSelection() {
            familySelectEl.value = $('input[name="familyResponsibleCheckbox"]:checked').val();
            $familySelectModalEl.modal('hide');
        }

        // Event bindings
        familySelectEl.addEventListener('mousedown', showFamilyModal);
        saveNewFamilyButtonEl.addEventListener('click', submitNewFamily);
        acceptFamilyModalButtonEl.addEventListener('click', submitFamilyModalSelection);
        btnReject.addEventListener('click', e => {
            invitationFormEl.querySelector('[name="state"]').value = 'rejected';
        });
        btnAccept.addEventListener('click', e => {
            invitationFormEl.querySelector('[name="state"]').value = 'accepted';
        });
        // if (typeof notFamily !== 'undefined') {
        //     $familySelectModalEl.modal({backdrop: 'static', keyboard: false});
        //     $(familyCreateModalEl).modal('show');
        // }
    });
});