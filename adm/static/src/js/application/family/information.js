odoo.define('adm.family.information', require => {
    "use strict";

    require('web.core');

    let counter = 0;

    function appendNewAddress(event) {
        counter--;

        const $clonedNewAddressTemplate = $('#template_application_family_home_addresss_card').clone(true);

        const $buttonToggleCollapse = $clonedNewAddressTemplate.find('[data-toggle="collapse"]')
        $buttonToggleCollapse[0].dataset.target = $buttonToggleCollapse[0].dataset.target + counter.toString();

        // const $divCollapse = $clonedNewAddressTemplate.find('.collapse');

        $clonedNewAddressTemplate.find('[data-filter-state]').each((i, el) => {
            el.dataset.filterState = el.dataset.filterState + counter.toString();
        })
        $clonedNewAddressTemplate.find('[id]').each((i, el) => {
            el.id = el.id + counter.toString();
        })
        $clonedNewAddressTemplate.find('[for]').each((i, el) => {
            el.for = el.for + counter.toString();
        })
        $clonedNewAddressTemplate.find('[name]').each((i, el) => {
            el.name = el.name + counter.toString();
        })

        // $divCollapse[0].id = $divCollapse[0].id + counter.toString();
        // We remove the style display none
        $clonedNewAddressTemplate.removeAttr('style');
        $clonedNewAddressTemplate.removeAttr('id');
        $clonedNewAddressTemplate.removeClass('d-none');
        $clonedNewAddressTemplate.addClass('mt-4');

        const addressList = document.getElementById('home_address_list');
        const newMany2manyRev = document.createElement('DIV');
        newMany2manyRev.dataset.admRel = "rel";
        $clonedNewAddressTemplate.appendTo(newMany2manyRev);
        // $clonedNewAddressTemplate.find('.js_remove_address').on('click', removeNewAddress);

        // Just a friky effect to make it cool ;)
        const $shownAddressCollapse = $(addressList).find('.collapse.show');
        // Hide shown relations

        function smoothScroll() {
            $("html, body").animate({ scrollTop: $clonedNewAddressTemplate.offset().top - 120 }, 800);
        }

        addressList.appendChild(newMany2manyRev);
        if ($shownAddressCollapse.length) {
            $shownAddressCollapse.on('hidden.bs.collapse', () => {
                $shownAddressCollapse.off('hidden.bs.collapse');
                smoothScroll();
            }).collapse('hide');
            $clonedNewAddressTemplate.find('.collapse').collapse('show');
        } else {
            $clonedNewAddressTemplate.find('.collapse').collapse('show');
            smoothScroll();
        }

    }
    function removeNewAddress(event) {
        $(event.currentTarget).closest('[data-adm-rel]').remove();
    }

    $(document).ready(() => {
        $('.js_add_address').on('click', appendNewAddress);
        $('.js_remove_address').on('click', removeNewAddress);
    });

})