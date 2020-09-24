var fv;
var tblMedicalParameters;
var tblMedicines;
var select_medicine;
var tblExams;
var input_lastperioddate;
var current_date;
var input_datejoined;

document.addEventListener('DOMContentLoaded', function (e) {
    const form = document.getElementById('frmDateMedical');
    fv = FormValidation.formValidation(form, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                // excluded: new FormValidation.plugins.Excluded(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                client: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un cliente'
                        },
                    }
                },
                treatment: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                    }
                },
                symptoms: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                    }
                },
                diagnosis: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                    }
                },
                total: {
                    validators: {
                        notEmpty: {},
                        numeric: {decimalSeparator: '.'}
                    }
                },
                lastperiod_date: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    },
                },
                date_joined: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    },
                },
            },
        }
    )
        .on('core.form.invalid', function () {
            $('a[href="#home"][data-toggle="tab"]').parent().find('i').removeClass().addClass('fas fa-times');
        })
        .on('core.element.validated', function (e) {
            var tab = e.element.closest('.tab-pane'),
                tabId = tab.getAttribute('id');
            if (e.valid) {
                const groupEle = FormValidation.utils.closest(e.element, '.form-group');
                if (groupEle) {
                    FormValidation.utils.classSet(groupEle, {
                        'has-success': false,
                    });
                }
                FormValidation.utils.classSet(e.element, {
                    'is-valid': false,
                });
                $('a[href="#' + tabId + '"][data-toggle="tab"]').parent().find('i').removeClass();
            } else {
                $('a[href="#' + tabId + '"][data-toggle="tab"]').parent().find('i').removeClass().addClass('fas fa-times');
            }
            const iconPlugin = fv.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            var tab = e.element.closest('.tab-pane'),
                tabId = tab.getAttribute('id');
            if (!e.result.valid) {
                // Query all messages
                const messages = [].slice.call(form.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
                $('a[href="#' + tabId + '"][data-toggle="tab"]').parent().find('i').removeClass();
            }
        })
        .on('core.form.valid', function () {
            var parameters = new FormData($(fv.form)[0]);

            var exams = tblExams.rows().data().toArray().filter(function (item, key) {
                return item.state === 1;
            });

            var medicalparameters = tblMedicalParameters.rows().data().toArray();

            console.log(medicalparameters);

            parameters.append('medicines', JSON.stringify(datemedical.details.medicines));
            parameters.append('exams', JSON.stringify(exams));
            parameters.append('medicalparameters', JSON.stringify(medicalparameters));
            parameters.append('action', 'add');
            submit_formdata_with_ajax('Alerta', '¿Estas seguro de realizar guardar la siguiente cita médica?', pathname, parameters, function () {
                alert_sweetalert('success', 'Notificación', 'Registro guardado correctamente', function () {
                    location.href = fv.form.getAttribute('data-url');
                }, 2000, null);
            }, function () {

            });
        });
});

var datemedical = {
    details: {
        medicines: []
    },
    calculate_invoice: function () {
        $.each(this.details.medicines, function (i, item) {
            item.pos = i;
            item.cant = parseInt(item.cant);
            item.subtotal = item.cant * parseFloat(item.price);
        });
    },
    add_medicines: function (item) {
        this.details.medicines.push(item);
        this.list_medicines();
    },
    list_medicines: function () {
        this.calculate_invoice();
        tblMedicines = $('#tblMedicines').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.details.medicines,
            columns: [
                {"data": "name"},
                {"data": "name"},
                {"data": "type.name"},
                {"data": "stock"},
                {"data": "cant"},
                {"data": "price"},
                {"data": "subtotal"},
            ],
            columnDefs: [
                {
                    targets: [0],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-xs btn-flat" style="color: white;"><i class="fas fa-trash-alt"></i></a>';
                    }
                },
                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<input type="text" class="form-control input-sm" autocomplete="off" name="cant" value="' + row.cant + '">';
                    }
                },
                {
                    targets: [-1, -2],
                    class: 'text-center',
                    orderable: false,
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
            ],
            rowCallback(row, data, displayNum, displayIndex, dataIndex) {
                var tr = $(row).closest('tr');

                tr.find('input[name="cant"]')
                    .TouchSpin({
                        min: 1,
                        max: parseInt(data.stock),
                    })
                    .keypress(function (e) {
                        return validate_form_text('numbers', e, null);
                    });
            },
        });
    },
    get_medicines_ids: function () {
        var ids = [];
        $.each(this.details.medicines, function (i, item) {
            ids.push(item.id);
        });
        return ids;
    },
};

function getMedicalParameters() {
    var parameters = {
        'action': 'get_parameters'
    };
    tblMedicalParameters = $('#tblMedicalParameters').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        paging: false,
        ordering: false,
        info: false,
        columns: [
            {data: "name"},
            {data: "valor"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    return '<input type="text" class="form-control" name="valorparameter" autocomplete="off" value="0.00">';
                }
            },
        ],
        rowCallback: function (row, data, index) {
            var tr = $(row).closest('tr');
            tr.find('input[name="valorparameter"]')
                .TouchSpin({
                    min: 0.00,
                    max: 1000000,
                    step: 0.01,
                    decimals: 2,
                    boostat: 5,
                    maxboostedstep: 10,
                })
                .keypress(function (e) {
                    return validate_form_text('numbers', e, null);
                });
        },
        initComplete: function (settings, json) {
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
}

function getExams() {
    var parameters = {
        'action': 'get_exams'
    };
    tblExams = $('#tblExams').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
        deferRender: true,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ""
        },
        paging: false,
        ordering: false,
        info: false,
        columns: [
            {data: "name"},
            {data: "state"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    return '<div class="checkbox"> <label><input type="checkbox" name="state" value=""></label></div>';
                }
            },
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
}

$(function () {

    current_date = new moment().format("YYYY-MM-DD");
    input_lastperioddate = $('input[name="lastperiod_date"]');
    select_medicine = $('select[name="searchmedicines"]');
    input_datejoined = $('input[name="date_joined"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    $('select[name="client"]').on('change.select2', function () {
        fv.revalidateField('client');
    });

    input_datejoined.datetimepicker({
        format: 'YYYY-MM-DD',
        useCurrent: false,
        locale: 'es',
        orientation: 'bottom',
        keepOpen: false
    });

    input_datejoined.datetimepicker('date', input_datejoined.val());

    input_datejoined.on('change.datetimepicker', function (e) {
        fv.revalidateField('date_joined');
    });

    input_lastperioddate.datetimepicker({
        useCurrent: false,
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        date: current_date,
    });

    input_lastperioddate.on('change.datetimepicker', function (e) {
        fv.revalidateField('lastperiod_date');
    });

    $('input[name="total"]')
        .TouchSpin({
            min: 0.00,
            max: 1000000,
            step: 0.01,
            decimals: 2,
            boostat: 5,
            maxboostedstep: 10,
            prefix: '$',
            verticalbuttons: true
        })
        .keypress(function (e) {
            return validate_decimals($(this), e);
        });

    // Medical Parameters

    getMedicalParameters();

    $('#tblMedicalParameters tbody')
        .on('change', 'input[name="valorparameter"]', function () {
            var td = tblMedicalParameters.cell($(this).closest('td, li')).index();
            var row = tblMedicalParameters.row(td.row).data();
            row.valor = parseInt($(this).val());
        });

    // Medicine

    select_medicine.select2({
        theme: "bootstrap4",
        language: 'es',
        allowClear: true,
        ajax: {
            delay: 250,
            type: 'POST',
            url: window.location.pathname,
            data: function (params) {
                var queryParameters = {
                    term: params.term,
                    action: 'search_medicine',
                    ids: JSON.stringify(datemedical.get_medicines_ids()),

                }
                return queryParameters;
            },
            processResults: function (data) {
                return {
                    results: data
                };
            },
        },
        placeholder: 'Ingrese una descripción',
        minimumInputLength: 1
    })
        .on('select2:select', function (e) {
            var medicine = e.params.data.data;
            medicine.cant = 1;
            datemedical.add_medicines(medicine);
            $(this).val('').trigger('change.select2');
        })
        .on('select2:clear', function (e) {
            $(this).val('').trigger('change.select2');
        });

    $('#tblMedicines tbody')
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblMedicines.cell($(this).closest('td, li')).index();
            alert_action('Notificación', '¿Estas seguro de eliminar el siguiente item de tu detalle?',
                function () {
                    datemedical.details.medicines.splice(tr.row, 1);
                    datemedical.list_medicines();
                }, function () {

                });
        })
        .on('change', 'input[name="cant"]', function () {
            var td = tblMedicines.cell($(this).closest('td, li')).index();
            var row = tblMedicines.row(td.row).data();
            datemedical.details.medicines[row.pos].cant = parseInt($(this).val());
            datemedical.calculate_invoice();
            var tr = $(this).parents('tr')[0];
            var subtotal = datemedical.details.medicines[row.pos].subtotal.toFixed(2);
            $('td:eq(6)', tr).html('$' + subtotal);
        });

    $('.btnClearMedicines').on('click', function () {
        select_medicine.val('').trigger('change.select2');
    });

    $('.btnDeleteAllMedicines').on('click', function () {
        if (datemedical.details.medicines.length === 0) return false;
        alert_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function () {
            datemedical.details.medicines = [];
            datemedical.list_medicines();
        }, function () {

        });
    });

    // tblExams

    getExams();

    $('#tblExams tbody')
        .on('change', 'input[name="state"]', function () {
            var td = tblExams.cell($(this).closest('td, li')).index();
            var row = tblExams.row(td.row).data();
            row.state = this.checked ? 1 : 0;
        });

});