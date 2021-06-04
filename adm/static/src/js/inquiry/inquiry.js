odoo.define('adm.inquiry', require => {
    "use strict"
    // TODO: Make this script work with Widgets

    // We just wait to some things to be done before using JQuery :)
    // This can be unneeded if we drop JQuery in this module (I hope some day...)
    require('web.core');

    let studentCount = 1;

    function filterGradeLevelsBySchoolCode(event) {
        const $currentTarget = $(event.currentTarget);
        const $selectGradeLevels = $currentTarget.parents('[role="tabpanel"]').find('[name="selStudentInterestGradeLevel"]');
        const schoolCodeId = $currentTarget.val();

        $selectGradeLevels.children("option:gt(0)").hide();
        $selectGradeLevels.children("option[data-school-code='" + schoolCodeId + "']").show();

        if ($selectGradeLevels.children("option:selected").is(":hidden")) {
            $selectGradeLevels.children("option:nth(0)").prop("selected", true);
        }
    }

    function filterSchoolYearsBySchoolCode(event) {
        const $currentTarget = $(event.currentTarget);
        const $selectStudentSchoolYear = $currentTarget.parents('[role="tabpanel"]').find('[name="selStudentSchoolYear"]');
        const schoolCodeId = $currentTarget.val();

        $selectStudentSchoolYear.children("option:gt(0)").hide();
        $selectStudentSchoolYear.children("option[data-schoolid='" + schoolCodeId + "']").show();

        if ($selectStudentSchoolYear.children("option:selected").is(":hidden")) {
            $selectStudentSchoolYear.children("option:nth(0)").prop("selected", true);
        }
    }

    function recomputaTabStudent() {
        $('#studentsNavbar').find('li').each((i, el) => {
            const $el = $(el);
            $el.children('a.student').html('Student '+(i+1)+'');
        });
        $('#studentsNavbar').find('li > a.student').last().click();
        $('#studentsCount').val($('#studentsNavbar').find('li > a').length-1);
    }
    function removeStudent(idStudent) {
        $(`#navStudent${idStudent}`).remove();
        $(`#student${idStudent}`).remove();
        recomputaTabStudent();
    }

    function addStudent() {
        studentCount++;
        var htmlTab =
            `<li class="nav-item" style="position: relative" id="navStudent${studentCount}">
        <a class="nav-link student" id="student${studentCount}-tab" data-toggle="tab" href="#student${studentCount}"
            role="tab" aria-controls="student${studentCount}" aria-selected="false">Student ${studentCount}</a>
            <i data-tabRemove="${studentCount}" class="fa fa-times remove-tab" style="position: absolute; top: -0.5em; right: 0.1em; font-size: 1.4em; color: orangered; cursor: pointer;""></i>
    </li>`;


        $(htmlTab).insertBefore($(this).parent());

        $('#studentsCount').val(studentCount);

        var studentClonnable = document.getElementById("student1").cloneNode(true);
        var studentTabContent = document.getElementById("studentsTabContent");

        studentTabContent.appendChild(studentClonnable);

        // Reassign ids
        $(studentClonnable).attr("id", "student" + studentCount);
        $(studentClonnable).attr("aria-labelledby", "student" + studentCount + "-tab");
        $(studentClonnable).removeClass("active");
        $(studentClonnable).removeClass("show");

        $(studentClonnable).find('input[id]').each((i, el) => {
            const $el = $(el);
            const newId = el.id + '-' + studentCount;
            $(studentClonnable).find(`label[for=${el.id}]`).attr('for', newId);
            el.id = newId
        });
//        $(studentClonnable).find("#txtStudent1FirstName").attr("id", "txtStudent" + studentCount + "FirstName")
//        $(studentClonnable).find("#txtStudent1MiddleName").attr("id", "txtStudent" + studentCount + "MiddleName")
//        $(studentClonnable).find("#txtStudent1LastName").attr("id", "txtStudent" + studentCount + "LastName")
//        $(studentClonnable).find("#txtStudent1Birthday").attr("id", "txtStudent" + studentCount + "Birthday")
//        $(studentClonnable).find("#selStudent1Gender").attr("id", "selStudent" + studentCount + "Gender")
//        $(studentClonnable).find("#selStudent1Nativelanguage").attr("id", "selStudent" + studentCount + "Nativelanguage")
//        $(studentClonnable).find("#selStudent1SchoolYear").attr("id", "selStudent" + studentCount + "SchoolYear")
//        $(studentClonnable).find("#selStudent1GradeLevel").attr("id", "selStudent" + studentCount + "GradeLevel")
//        $(studentClonnable).find("#selStudent1CurrentGradeLevel").attr("id", "selStudent" + studentCount + "CurrentGradeLevel")
//        $(studentClonnable).find("#txtStudent1CurrentSchool").attr("id", "txtStudent" + studentCount + "CurrentSchool")
//        $(studentClonnable).find("#txtStudent1FromEnglishSchool").attr("id", "txtStudent" + studentCount + "FromEnglishSchool")
//        $(studentClonnable).find("#txtStudent1FromEnglishSchool").attr("label", "txtStudent" + studentCount + "FromEnglishSchool")
//        $(studentClonnable).find(".txtStudent1ExtraServices").attr("name", "txtStudent" + studentCount + "ExtraServices")
//        $(studentClonnable).find(".txtStudent1ExtraServices").attr("id", "txtStudent" + studentCount + "ExtraServices")
//        $(studentClonnable).find("#fileStudent1Photo").attr("name", "fileStudent" + studentCount + "Photo")
//        $(studentClonnable).find("#fileStudent1BirthCert").attr("name", "fileStudent" + studentCount + "BirthCert")
//        $(studentClonnable).find("#fileStudent1ReportCard").attr("name", "fileStudent" + studentCount + "ReportCard")
//        $(studentClonnable).find("#fileStudent1ImmunizationRecord").attr("name", "fileStudent" + studentCount + "ImmunizationRecord")

        $(studentClonnable).find("input").each(function () {
            var input_type = $(this).attr("type")
            if (input_type == "checkbox") {
                this.checked = false
            } else {
                $(this).val("");
            }
        });


        document.querySelectorAll(".selectSchoolYear").forEach(function (element) {
            element.addEventListener("change", function () {
                var schoolCodeID = $(this).find("option:selected").data("school_code");
                $(this).parent().next().find("select option").each(function (element) {
                    var school_option_id = $(this).data("school_code");
                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                $(this).parent().next().find("select").val(-1);
            })
        });
        recomputaTabStudent();
        $(studentClonnable).find('select[name="selStudentSchoolCode"]').on('click', filterGradeLevelsBySchoolCode).trigger('change');
        $(studentClonnable).find('select[name="selStudentSchoolCode"]').on('click', filterSchoolYearsBySchoolCode).trigger('change');
    }

    function showOnlyCountrysStates() {
        // You might ask, why don't use # selector instead of getElementById
        // The reason for that is getElementById uses native code, so is much faster
        // And passing to jquery an element, it doesn't try to find it.
        // So... $(getElementById) has better performance and allow us to use JQuery :)

        const selectState = $(document.getElementById('selState'));
        const selectCountry = document.getElementById('selCountry');

        selectState.children("option:gt(0)").hide();
        selectState.children("option[data-country='" + selectCountry.value + "']").show();

        if (selectState.children("option:selected").is(":hidden")) {
            selectState.children("option:nth(0)").prop("selected", true);
        }
    }

    function toggleDataParents() {
        const checkboxFamilyIdEl = document.getElementById('checkbox_family_id');
        const familyExists = checkboxFamilyIdEl.checked;
        
        const familySectionElList = document.querySelectorAll('.hide_parent');
        
        const inputFamilyIdEl = document.getElementById('input_family_id');
        const selFamilyIdTypeEl = document.getElementById('selFamilyIDType');
        
        for (let familySectionEl of familySectionElList) {
            // We toggle parent sections 
            familySectionEl.classList.toggle('d-none', familyExists);
            // We disable all inputs & select into parent sections
            for (let formInputEl of familySectionEl.querySelectorAll('input,select')) {
                formInputEl.disabled = familyExists;
            }
        }
        
        if (inputFamilyIdEl) {
            inputFamilyIdEl.classList.toggle('d-none', !familyExists);
            for (let formInputEl of inputFamilyIdEl.querySelectorAll('input,select')) {
                formInputEl.disabled = !familyExists;
            }
        }
        
        if (selFamilyIdTypeEl) {
            selFamilyIdTypeEl.classList.toggle('d-none', !familyExists);
        }
    }

    function toggleSecondParent() {
        const sectionParent2El = document.getElementById("section_parent_2");
        if (sectionParent2El) {
            sectionParent2EL.classlist.toggle('d-none');
            for (let formInputEl of sectionParent2El.querySelectorAll('input,select')) {
                formInputEl.disabled = !formInputEl.disabled;
            }
        }
    }

    function invoiceAddress(valor) {
        var status = valor.data
        
        const txtInvoiceAddress1El = document.querySelector("input[name='txtInvoiceAddress_1']");
        const txtInvoiceAddress2El = document.querySelector("input[name='txtInvoiceAddress_2']");
        
        if (txtInvoiceAddress1El) {
            txtInvoiceAddress1El.checked = (status == 1);
        }
        
        if (txtInvoiceAddress2El) {
            txtInvoiceAddress2El.checked = (status == 2);
        }
    }

    $(document).ready(function () {
        // Format Init data :P
        showOnlyCountrysStates();

        // Event Handlers
        //document.getElementById("add-tab").addEventListener("click", addStudent);
        $(document.getElementById("selCountry")).on("change", showOnlyCountrysStates);

        $(document.getElementById('showSecondParent')).on('click', toggleSecondParent);

        $('#checkbox_family_id').on('click', toggleDataParents)
        $('#txtInvoiceAddress_1').click(1,invoiceAddress)
        $('#txtInvoiceAddress_2').click(2,invoiceAddress)

        $('#add-tab').on('click',addStudent)

        $(document).on('click', '.remove-tab', function () {
            removeStudent($(this).attr('data-tabRemove'))
        });


        document.querySelectorAll(".custom-file-input").forEach(function (element) {
            element.addEventListener("change", function () {
                var fileName = this.files[0].name
                $(this).next("label").text(fileName);
            })
        })
        document.querySelectorAll(".selectSchoolYear").forEach(function (element) {
            element.addEventListener("change", function () {
                var schoolCodeID = $(this).find("option:selected").data("school_code");
                $(this).parent().next().find("select option").each(function (element) {
                    var school_option_id = $(this).data("school_code");
                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                $(this).parent().next().find("select").val(-1);
            })
        });
        document.querySelectorAll("#selSource").forEach(function (element) {
            element.addEventListener("change", function () {
                if ($(this).find("option:selected").data("other") != undefined)
                    $("#contOtherSource").removeClass("d-none")
                else
                    $("#contOtherSource").addClass("d-none")
            })
        });
        $('select[name="selStudentSchoolCode"]').on('change', filterGradeLevelsBySchoolCode).trigger('change');
        $('select[name="selStudentSchoolCode"]').on('change', filterSchoolYearsBySchoolCode).trigger('change');
        console.log('asdasd');
    });

    // Get user location
    $.get('/adm/geolocation').then(result => {
        if (!_.isEmpty(result)) {
            // Country
            const $selCountry = $('[name^=selCountry]');
            $selCountry.each((i, selCountry) => {
                const countryOption = _.filter(selCountry.options, option => option.dataset.code === result.country_code)
                if (countryOption.length) {
                    selCountry.value = countryOption[0].value;

                    // State
                    const $selState = $('[name^=selState]');
                    $selState.each((i, selState) => {

                        const stateOption = _.filter(selCountry.options, option => option.dataset.country === countryOption[0].value
                                                     && option.dataset.code === result.region)
                        if (stateOption.length) {
                            selState.value = stateOption[0].value;
                        }
                    });
                }
            });
            showOnlyCountrysStates();
        }
    })
})
