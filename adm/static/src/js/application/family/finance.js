odoo.define('adm.family.finance', require => {
    "use strict";

    require('web.core');

    let counter = 0;

    function addNewResFinanceItem(event) {
        counter--;

        const $clonedNewResFinanceItemTemplate = $('#template_application_family_finance_res_item').clone();

        $clonedNewResFinanceItemTemplate.find('[id]').each((i, el) => {
            el.id = el.id + counter.toString();
        })
        $clonedNewResFinanceItemTemplate.find('[for]').each((i, el) => {
            el.for = el.for + counter.toString();
        })
        $clonedNewResFinanceItemTemplate.find('[name]').each((i, el) => {
            el.name = el.name + counter.toString();
        })

        // $divCollapse[0].id = $divCollapse[0].id + counter.toString();
        // We remove the style display none
        $clonedNewResFinanceItemTemplate.removeAttr('style');
        $clonedNewResFinanceItemTemplate.removeAttr('id');
        $clonedNewResFinanceItemTemplate.removeClass('d-none');

        const resFinanceItemList = document.getElementById('js_add_res_finance_item');
        $clonedNewResFinanceItemTemplate.find('.js_remove_item').on('click', removeNewResFinanceItem);

        // Just a friky effect to make it cool ;)
        // Hide shown relations

        function smoothScroll() {
            $("html, body").animate({ scrollTop: $clonedNewResFinanceItemTemplate.offset().top - 120 }, 800);
        }
        $clonedNewResFinanceItemTemplate.insertBefore(resFinanceItemList);
        // if ($shownResFinanceItemCollapse.length) {
        //     $shownResFinanceItemCollapse.on('hidden.bs.collapse', () => {
        //         $shownResFinanceItemCollapse.off('hidden.bs.collapse');
        //         smoothScroll();
        //     }).collapse('hide');
        //     $clonedNewResFinanceItemTemplate.find('.collapse').collapse('show');
        // } else {
        //     $clonedNewResFinanceItemTemplate.find('.collapse').collapse('show');
        //     smoothScroll();
        // }

    }
    function removeNewResFinanceItem(event) {
        $(event.currentTarget).closest('[data-adm-rel]').remove();
    }

    $(document).ready(() => {
        $('#js_add_res_finance_item button').on('click', addNewResFinanceItem)
        $('.js_remove_item').on('click', removeNewResFinanceItem);
    });

})