var tblProducts;
var tblSearchProd;
var client = {};
var product;
var fvSale;
var fvClient;
var input_datejoined;
var input_endate;
var input_birthdate;
var current_date;
var select_client;
var select_parish;

var vents = {
    details: {
        client: '',
        date_joined: '',
        end_date: '',
        subtotal: 0.00,
        iva: 0.00,
        dscto: 0.00,
        total: 0.00,
        payment: 0,
        products: [],
    },
    calculate_invoice: function () {
        var subtotal = 0.00;
        $.each(this.details.products, function (i, item) {
            item.pos = i;
            item.cant = parseInt(item.cant);
            item.subtotal = item.cant * parseFloat(item.price);
            subtotal += item.subtotal;
        });
        vents.details.subtotal = subtotal;
        vents.details.iva = subtotal * iva;
        vents.details.total = subtotal + vents.details.iva;
        $('input[name="subtotal"]').val(vents.details.subtotal.toFixed(2));
        $('input[name="iva"]').val(vents.details.iva.toFixed(2));
        $('input[name="total"]').val(vents.details.total.toFixed(2));
    },
    list_products: function () {
        this.calculate_invoice();
        tblProducts = $('#tblProducts').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            data: this.details.products,
            ordering: false,
            lengthChange: false,
            searching: false,
            paginate: false,
            columns: [
                {data: "id"},
                {data: "name"},
                {data: "type.name"},
                {data: "stock"},
                {data: "cant"},
                {data: "price"},
                {data: "subtotal"},
            ],
            columnDefs: [
                {
                    targets: [-4],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<span class="badge badge-secondary">' + data + '</span>';
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
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<input type="text" class="form-control input-sm" autocomplete="off" name="price" value="' + row.price + '">';
                    }
                },
                {
                    targets: [0],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '<a rel="remove" class="btn btn-danger btn-flat btn-xs"><i class="fa fa-trash fa-1x"></i></a>';
                    }
                },
            ],
            rowCallback: function (row, data, index) {
                var frm = $(row).closest('tr');

                frm.find('input[name="cant"]')
                    .TouchSpin({
                        min: 1,
                        max: data.stock,
                    })
                    .keypress(function (e) {
                        return validate_form_text('numbers', e, null);
                    });

                frm.find('input[name="price"]')
                    .TouchSpin({
                        min: 0.00,
                        max: 1000000,
                        step: 0.01,
                        decimals: 2,
                        boostat: 5,
                        maxboostedstep: 10,
                    })
                    .keypress(function (e) {
                        return validate_decimals($(this), e);
                    });

            },
            initComplete: function (settings, json) {

            },
        });
    },
    get_products_ids: function () {
        var ids = [];
        $.each(this.details.products, function (i, item) {
            ids.push(item.id);
        });
        return ids;
    },
    add_product: function (item) {
        this.details.products.push(item);
        this.list_products();
    },
};


document.addEventListener('DOMContentLoaded', function (e) {
    const frmSale = document.getElementById('frmSale');
    fvSale = FormValidation.formValidation(frmSale, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                excluded: new FormValidation.plugins.Excluded(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                date_joined: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    }
                },
                client: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un cliente'
                        },
                    }
                },
            },
        }
    )
        .on('core.element.validated', function (e) {
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
            }
            const iconPlugin = fvSale.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(frmSale.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            if ($.isEmptyObject(client)) {
                message_error('Debe tener un cliente seleccionado');
                $('input[name="search_cli"]').focus().select();
                return false;
            }

            vents.details.client = client.id;
            vents.details.date_joined = $('input[name="date_joined"]').val();
            vents.details.end_date = $('input[name="end_date"]').val();
            vents.details.payment = $('select[name="payment"]').val();

            if (vents.details.products.length === 0) {
                message_error('Debe tener al menos un item en el detalle de la venta');
                return false;
            }

            submit_with_ajax('Notificación',
                '¿Estas seguro de guardar la siguiente compra?',
                pathname,
                {
                    'action': $('input[name="action"]').val(),
                    'items': JSON.stringify(vents.details)
                },
                function (request) {
                    //printInvoice(request.id);
                    location.href = frmSale.getAttribute('data-url');
                },
            );
        });
});

document.addEventListener('DOMContentLoaded', function (e) {
    const frmClient = document.getElementById('frmClient');
    fvClient = FormValidation.formValidation(frmClient, {
            locale: 'es_ES',
            localization: FormValidation.locales.es_ES,
            plugins: {
                trigger: new FormValidation.plugins.Trigger(),
                submitButton: new FormValidation.plugins.SubmitButton(),
                bootstrap: new FormValidation.plugins.Bootstrap(),
                icon: new FormValidation.plugins.Icon({
                    valid: 'fa fa-check',
                    invalid: 'fa fa-times',
                    validating: 'fa fa-refresh',
                }),
            },
            fields: {
                first_name: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                        regexp: {
                            regexp: /^([A-Za-zÁÉÍÓÚñáéíóúÑ]{0}?[A-Za-zÁÉÍÓÚñáéíóúÑ\']+[\s])+([A-Za-zÁÉÍÓÚñáéíóúÑ]{0}?[A-Za-zÁÉÍÓÚñáéíóúÑ\'])+?$/i,
                            message: 'Debe ingresar sus dos nombres y solo utilizando caracteres alfabéticos'
                        },
                    }
                },
                last_name: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 2,
                        },
                        regexp: {
                            regexp: /^([A-Za-zÁÉÍÓÚñáéíóúÑ]{0}?[A-Za-zÁÉÍÓÚñáéíóúÑ\']+[\s])+([A-Za-zÁÉÍÓÚñáéíóúÑ]{0}?[A-Za-zÁÉÍÓÚñáéíóúÑ\'])+?$/i,
                            message: 'Debe ingresar sus dos apellidos y solo utilizando caracteres alfabéticos'
                        },
                    }
                },
                dni: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 1,
                        },
                        digits: {},
                        remote: {
                            url: pathname,
                            // Send { username: 'its value', email: 'its value' } to the back-end
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="dni"]').value,
                                    type: 'dni',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El número de cedula ya se encuentra registrado',
                            method: 'POST'
                        }
                    }
                },
                email: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 5
                        },
                        regexp: {
                            regexp: /^([a-z0-9_\.-]+)@([\da-z\.-]+)\.([a-z\.]{2,6})$/i,
                            message: 'El formato del email no es correcto'
                        },
                        remote: {
                            url: pathname,
                            // Send { username: 'its value', email: 'its value' } to the back-end
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="email"]').value,
                                    type: 'email',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El email ya se encuentra registrado',
                            method: 'POST'
                        }
                    }
                },
                image: {
                    validators: {
                        file: {
                            extension: 'jpeg,jpg,png',
                            type: 'image/jpeg,image/png',
                            maxFiles: 1,
                            message: 'Introduce una imagen válida'
                        }
                    }
                },
                gender: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione un genero',
                        },
                    }
                },
                mobile_phone: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 10
                        },
                        digits: {},
                        remote: {
                            url: pathname,
                            // Send { username: 'its value', email: 'its value' } to the back-end
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="mobile_phone"]').value,
                                    type: 'mobile_phone',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El número de teléfono celular ya se encuentra registrado',
                            method: 'POST'
                        }
                    }
                },
                landline: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 7
                        },
                        digits: {},
                        remote: {
                            url: pathname,
                            // Send { username: 'its value', email: 'its value' } to the back-end
                            data: function () {
                                return {
                                    obj: frmClient.querySelector('[name="mobile_phone"]').value,
                                    type: 'landline',
                                    action: 'validate_client'
                                };
                            },
                            message: 'El número de teléfono convencional ya se encuentra registrado',
                            method: 'POST'
                        }
                    }
                },
                address: {
                    validators: {
                        notEmpty: {},
                        stringLength: {
                            min: 4,
                        }
                    }
                },
                birthdate: {
                    validators: {
                        notEmpty: {
                            message: 'La fecha es obligatoria'
                        },
                        date: {
                            format: 'YYYY-MM-DD',
                            message: 'La fecha no es válida'
                        }
                    }
                },
                parish: {
                    validators: {
                        notEmpty: {
                            message: 'Seleccione una parroquia',
                        },
                    }
                },
                password: {
                    validators: {
                        notEmpty: {
                            message: 'Se requiere la contraseña'
                        }
                    }
                },
            },
        }
    )
        .on('core.element.validated', function (e) {
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
            }
            const iconPlugin = fvClient.getPlugin('icon');
            const iconElement = iconPlugin && iconPlugin.icons.has(e.element) ? iconPlugin.icons.get(e.element) : null;
            iconElement && (iconElement.style.display = 'none');
        })
        .on('core.validator.validated', function (e) {
            if (!e.result.valid) {
                const messages = [].slice.call(frmClient.querySelectorAll('[data-field="' + e.field + '"][data-validator]'));
                messages.forEach((messageEle) => {
                    const validator = messageEle.getAttribute('data-validator');
                    messageEle.style.display = validator === e.validator ? 'block' : 'none';
                });
            }
        })
        .on('core.form.valid', function () {
            var parameters = {};
            $.each($(fvClient.form).serializeArray(), function (key, item) {
                parameters[item.name] = item.value;
            });
            parameters['action'] = 'create_client';
            submit_with_ajax('Notificación', '¿Estas seguro de realizar la siguiente acción?', pathname,
                parameters,
                function () {
                    $('#myModalAddClient').modal('hide');
                }
            );
        });
});


function printInvoice(id) {
    var printWindow = window.open("/erp/crm/sale/print/invoice/" + id + "/", 'Print', 'left=200, top=200, width=950, height=500, toolbar=0, resizable=0');
    printWindow.addEventListener('load', function () {
        printWindow.print();
    }, true);
}


$(function () {

    current_date = new moment().format("YYYY-MM-DD");
    input_datejoined = $('input[name="date_joined"]');
    input_endate = $('input[name="end_date"]');
    select_client = $('select[name="client"]');
    input_birthdate = $('input[name="birthdate"]');
    select_parish = $('select[name="parish"]');

    $('.select2').select2({
        theme: 'bootstrap4',
        language: "es",
    });

    $('select[name="payment"]')
        .on('change.select2', function () {
            fvSale.revalidateField('payment');
            var id = $(this).val();
            var start_date = input_datejoined.val();
            input_endate.datetimepicker('minDate', start_date);
            input_endate.datetimepicker('date', start_date);
            formGroupCredit.hide();
            if (id === 'credito') {
                formGroupCredit.show();
            }
        });

    $('.btnRemoveAll').on('click', function () {
        if (vents.details.products.length === 0) return false;
        dialog_action('Notificación', '¿Estas seguro de eliminar todos los items de tu detalle?', function () {
            var removeValFromIndex = [];
            $.each(vents.details.products, function (k, v) {
                if (!v.hasOwnProperty('state')) {
                    removeValFromIndex.push(v.pos);
                }
            });
            for (var i = removeValFromIndex.length - 1; i >= 0; i--) {
                vents.details.products.splice(removeValFromIndex[i], 1);
            }
            vents.list_products();
        });
    });

    /* Products */

    $('input[name="search"]').autocomplete({
        source: function (request, response) {
            $.ajax({
                url: pathname,
                data: {
                    'action': 'search_products',
                    'term': request.term,
                    'ids': JSON.stringify(vents.get_products_ids()),
                },
                dataType: "json",
                type: "POST",
                beforeSend: function () {

                },
                success: function (data) {
                    response(data);
                }
            });
        },
        min_length: 3,
        delay: 300,
        select: function (event, ui) {
            event.preventDefault();
            $(this).blur();
            if (ui.item.stock === 0) {
                message_error('El stock de este producto esta en 0');
                return false;
            }
            ui.item.cant = 1;
            vents.add_product(ui.item);
            $(this).val('').focus();
        }
    });

    $('.btnClear').on('click', function () {
        $('input[name="search"]').val('').focus();
    });

    $('#tblProducts tbody')
        .on('change', 'input[name="cant"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.details.products[tr.row].cant = parseInt($(this).val());
            vents.calculate_invoice();
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + vents.details.products[tr.row].subtotal.toFixed(2));
        })
        .on('change', 'input[name="price"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.details.products[tr.row].price = parseFloat($(this).val());
            vents.calculate_invoice();
            $('td:eq(6)', tblProducts.row(tr.row).node()).html('$' + vents.details.products[tr.row].subtotal.toFixed(2));
        })
        .on('click', 'a[rel="remove"]', function () {
            var tr = tblProducts.cell($(this).closest('td, li')).index();
            vents.details.products.splice(tr.row, 1);
            vents.list_products();
        });

    $('.btnSearch').on('click', function () {
        tblSearchProd = $('#tblSearchProd').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search_products',
                    'term': $('input[name="search"]').val(),
                    'ids': JSON.stringify(vents.get_products_ids()),
                },
                dataSrc: ""
            },
            //paging: false,
            //ordering: false,
            //info: false,
            columns: [
                {data: "name"},
                {data: "type.name"},
                {data: "price"},
                {data: "stock"},
                {data: "id"},
            ],
            columnDefs: [
                {
                    targets: [-3],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return '$' + parseFloat(data).toFixed(2);
                    }
                },
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        if (row.stock > 0) {
                            return '<span class="badge badge-success">' + data + '</span>'
                        }
                        return '<span class="badge badge-warning">' + data + '</span>'
                    }
                },
                {
                    targets: [-1],
                    class: 'text-center',
                    render: function (data, type, row) {
                        if (row.stock > 0) {
                            return '<a rel="add" class="btn btn-secondary btn-flat btn-xs"><i class="fas fa-plus"></i></a>'
                        }
                        return 'No se puede agregar'
                    }
                }
            ],
            rowCallback: function (row, data, index) {
                var tr = $(row).closest('tr');
                if (data.stock === 0) {
                    $(tr).css({'background': '#dc3345', 'color': 'white'});
                }
            },
        });
        $('#myModalSearchProd').modal('show');
    });

    $('#tblSearchProd tbody').on('click', 'a[rel="add"]', function () {
        var row = tblSearchProd.row($(this).parents('tr')).data();
        row.cant = 1;
        vents.add_product(row);
        tblSearchProd.row($(this).parents('tr')).remove().draw();
    });

    /* Client */

    select_client.select2({
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
                    action: 'search_client'
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
        minimumInputLength: 1,
    })
        .on('select2:select', function (e) {
            client = e.params.data.data;
            console.log(client);
            fvSale.revalidateField('client');
        })
        .on('select2:clear', function (e) {
            fvSale.revalidateField('client');
        });

    $('.btnAddClient').on('click', function () {
        $('#myModalAddClient').modal('show');
    });

    $('#myModalAddClient').on('hidden.bs.modal', function () {
        fvClient.resetForm(true);
    });

    input_birthdate.datetimepicker({
        format: 'YYYY-MM-DD',
        locale: 'es',
        keepOpen: false,
        date: new moment().format("YYYY-MM-DD")
    });

    input_birthdate.datetimepicker('date', input_birthdate.val());

    input_birthdate.on('change.datetimepicker', function (e) {
        fvClient.revalidateField('birthdate');
    });

    $('input[name="dni"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });

    $('input[name="first_name"]').keypress(function (e) {
        return validate_form_text('letters', e, null);
    });

    $('input[name="last_name"]').keypress(function (e) {
        return validate_form_text('letters', e, null);
    });

    $('input[name="mobile_phone"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });

    $('input[name="landline"]').keypress(function (e) {
        return validate_form_text('numbers', e, null);
    });

    $('select[name="gender"]').on('change.select2', function () {
        fvClient.revalidateField('gender');
    });

    select_parish.select2({
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
                    action: 'search_parish'
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
        minimumInputLength: 1,
    })
        .on('select2:select', function (e) {
            console.log(e.params.data);
            fvClient.revalidateField('parish');
        })
        .on('select2:clear', function (e) {
            fvClient.revalidateField('parish');
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
        fvSale.revalidateField('date_joined');
        input_endate.datetimepicker('minDate', e.date);
        input_endate.datetimepicker('date', e.date);
    });

    fvSale.revalidateField('client')
        .then(function (status) {
            fvSale.resetForm(true);
            input_datejoined.datetimepicker('date', current_date);
        });
});