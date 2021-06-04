odoo.define('adm.application.create', require => {
    "use strict";

    require('web.core');
    const rpc = require('web.rpc');

    document.addEventListener('DOMContentLoaded', () => {
        // Variable and DOM elements
        const formCreateApplication = document.getElementById('form_create_application');
        const userPartnerId = parseInt(document.querySelector('meta[name="_user_partner_id"]').getAttribute('value'));

        const familySelectModalCreateEl = document.getElementById('family_select_modal_create');


        const notBelongToThisFamiliyInputEl = document.getElementById('notBelongToThisFamiliy');

        // Family Selection elements
        const selectFamilyEl = document.getElementById('family_select_modal');
        const $selectFamilyEl = $(selectFamilyEl);

        const acceptFamilyModalButtonEl = document.querySelector('.js_accept_family_modal');
        const $familySelectModalCreateEl = $(familySelectModalCreateEl);
        const familyUlList = document.querySelector('.o_adm_family_selection ul');

        // Modal new family elements
        const newFamilyNameInputEl = document.getElementById('newFamilyName');
        const otherResponsibleEmailEl = document.getElementById('otherResponsibleEmail');
        const saveNewFamilyButtonEl = document.querySelector('.js_save_new_family');

        // Event functions
        function toggleBelongFamily(event) {
            const checkboxEl = event.currentTarget;

            const toggle = checkboxEl.checked;
            $('.js_new_family_form').toggleClass('d-none', toggle);
            $('.js_other_family_responsible_email').toggleClass('d-none', !toggle);
            document.getElementById('otherResponsibleEmail').toggleAttribute('disabled', !toggle);
        }

        function submitFamilyModalSelection() {
            const familyID = $('input[name="familyResponsibleCheckbox"]:checked').val();
            document.querySelector('input[name="family_id"]').value = familyID;
            $selectFamilyEl.modal('hide');
        }

        async function submitNewFamily() {
            if (notBelongToThisFamiliyInputEl.checked) {
                // Sending email family responsible
                const inviteMailsJSONListInputEl = document.querySelector('input[name="invite_mail_json_list"]');
                const inviteMailsJSONList = JSON.parse(inviteMailsJSONListInputEl.value);

                inviteMailsJSONList.push({
                    email: otherResponsibleEmailEl.value,
                    access: [1,2,3,4]
                });
                inviteMailsJSONListInputEl.value = JSON.stringify(inviteMailsJSONList);
            } else {
                // Creating a new family for the students
                const familyPartnerId = await rpc.query({
                    model: 'res.partner',
                    method: 'create',
                    args: [{
                        'name': newFamilyNameInputEl.value,
                        'is_family': true,
                        'is_company': true,
                        'member_ids': [[4, userPartnerId, false]]
                    }]
                });

                await rpc.query({
                    model: 'res.partner',
                    method: 'write',
                    args: [[userPartnerId], {
                        'family_ids': [[4, familyPartnerId, false]]
                    }],
                });

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
                console.log('Created new family: ' + familyPartnerId);
            }
            $familySelectModalCreateEl.modal('hide');
        }

        // Binding events
        notBelongToThisFamiliyInputEl.addEventListener('change', toggleBelongFamily);
        acceptFamilyModalButtonEl.addEventListener('click', submitFamilyModalSelection);
        saveNewFamilyButtonEl.addEventListener('click', submitNewFamily);

        // Showing modal
        $selectFamilyEl.modal({backdrop: 'static', keyboard: false});
        // $('.o_adm_family_select_item').on('click', event => {
        //     const familyItemEl = event.currentTarget;
        //     $('input[name="family_id"]').val(familyItemEl.dataset.familyId);
        //     $selectModal.modal('hide');
        // });
        // $selectModal.modal({backdrop: 'static', keyboard: false});
    });
});