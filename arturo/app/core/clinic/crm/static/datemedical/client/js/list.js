var tblDateMedical;
var date_current;
var date_range = null;

function getData() {
    var parameters = {
        'action': 'search',
        'start_date': date_current,
        'end_date': date_current,
    };

    if (date_range != null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tblDateMedical = $('#data').DataTable({
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
        order: [[ 5, "desc" ]],
        columns: [
            {data: "pos"},
            {data: "client.full_name"},
            {data: "date_joined"},
            {data: "hour"},
            {data: "lastperiod_date"},
            {data: "weekday"},
            {data: "status.name"},
            {data: "id"},
        ],
        columnDefs: [
            {
                targets: [-2],
                class: 'text-center',
                render: function (data, type, row) {
                    var html = '';
                    switch (row.status.id) {
                        case 'activo':
                            html = '<span class="badge badge-info">' + data + '</span>'
                            break;
                        case 'cancelado':
                            html = '<span class="badge badge-warning">' + data + '</span>'
                            break;
                        case 'finalizado':
                            html = '<span class="badge badge-success">' + data + '</span>'
                            break;
                        case 'eliminado':
                            html = '<span class="badge badge-danger">' + data + '</span>'
                            break;
                    }
                    return html;
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    var buttons = '';
                    if (row.status.id === 'activo') {
                        buttons += '<a class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Cancelar" rel="cancel"><i class="fas fa-times"></i></a> ';
                    }
                    buttons += '<a class="btn btn-info btn-xs btn-flat" data-toggle="tooltip" title="Detalles" rel="det"><i class="fas fa-folder-open"></i></a> ';
                    buttons += '<a href="/clinic/crm/date/medical/client/print/' + row.id + '/" target="_blank" class="btn btn-secondary btn-xs btn-flat" data-toggle="tooltip" title="Imprimir"><i class="fas fa-file-pdf"></i></a> ';
                    return buttons;
                }
            },
            {
                targets: [-3],
                class: 'text-center',
                render: function (data, type, row) {
                    return data;
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

    date_current = new moment().format("YYYY-MM-DD");

    $('input[name="date_range"]')
        .daterangepicker({
            language: 'auto',
            startDate: new Date(),
            locale: {
                format: 'YYYY-MM-DD',
            }
        })
        .on('apply.daterangepicker', function (ev, picker) {
            date_range = picker;
            getData();
        });

    $('#data tbody')
        .on('click', 'a[rel="cancel"]', function () {
            $('.tooltip').remove();
            var tr = tblDateMedical.cell($(this).closest('td, li')).index();
            var rows = tblDateMedical.row(tr.row).data();

            submit_with_ajax('Alerta', '¿Estas seguro de cancelar la cita?', pathname, {
                'action': 'cancel_cite',
                'id': rows.id,
            }, function () {
                alert_sweetalert('info', 'Alerta', 'Se ha cancelado con exito la cita', function () {
                    tblDateMedical.ajax.reload();
                }, 3000, null);
            });

            console.log(rows);
        })
        .on('click', 'a[rel="det"]', function () {
            $('.tooltip').remove();
            var cell = tblDateMedical.cell($(this).closest('td, li')).index();
            var data = tblDateMedical.row(cell.row).data();
            $('.nav-tabs a[href="#home"]').tab('show');

            var datemedical = [];
            datemedical.push({'id': 'Cliente', 'name': data.client.full_name});
            datemedical.push({'id': 'Fecha de registro', 'name': data.date_joined});
            datemedical.push({'id': 'Hora', 'name': data.hour});
            datemedical.push({'id': 'Fecha de último periodo', 'name': data.lastperiod_date});
            datemedical.push({'id': 'Sintomas', 'name': data.symptoms});
            datemedical.push({'id': 'Diagnóstico', 'name': data.diagnosis});
            datemedical.push({'id': 'Tratamiento', 'name': data.treatment});
            datemedical.push({'id': 'Valor', 'name': '$' + parseFloat(data.total).toFixed(2)});


            $('#tblDateMedical').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                data: datemedical,
                paging: false,
                info: false,
                searching: false,
                columns: [
                    {"data": "id"},
                    {"data": "name"},
                ],
                columnDefs: [
                    {
                        targets: [0],
                        class: 'text-left',
                        render: function (data, type, row) {
                            return '<b>' + data + '</b>';
                        }
                    },
                ],
                rowCallback: function (row, data, index) {

                },
                initComplete: function (settings, json) {
                    $('[data-toggle="tooltip"]').tooltip();
                }
            });
            $('#tblExams').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_exams',
                        'id': data.id
                    },
                    dataSrc: ""
                },
                paging: false,
                ordering: false,
                info: false,
                columns: [
                    {data: "exam.name"},
                ],
                columnDefs: [
                    {
                        targets: [0],
                        class: 'text-left',
                        render: function (data, type, row) {
                            return data;
                        }
                    },
                ],
                rowCallback: function (row, data, index) {

                },
                initComplete: function (settings, json) {

                }
            });
            $('#tblMedicines').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_medicines',
                        'id': data.id
                    },
                    dataSrc: ""
                },
                paging: false,
                ordering: false,
                info: false,
                columns: [
                    {data: "product.name"},
                    {data: "product.type.name"},
                    {data: "price"},
                    {data: "cant"},
                    {data: "subtotal"},
                ],
                columnDefs: [
                    {
                        targets: [-1, -3],
                        class: 'text-center',
                        render: function (data, type, row) {
                            return '$' + parseFloat(data).toFixed(2);
                        }
                    },
                ],
                rowCallback: function (row, data, index) {

                },
                initComplete: function (settings, json) {

                }
            });
            $('#tblMedicalParameters').DataTable({
                responsive: true,
                autoWidth: false,
                destroy: true,
                deferRender: true,
                ajax: {
                    url: pathname,
                    type: 'POST',
                    data: {
                        'action': 'search_medicalparameter',
                        'id': data.id
                    },
                    dataSrc: ""
                },
                paging: false,
                ordering: false,
                info: false,
                columns: [
                    {data: "medicalparameters.name"},
                    {data: "valor"},
                ],
                columnDefs: [
                    {
                        targets: [-1],
                        class: 'text-left',
                        render: function (data, type, row) {
                            return data;
                        }
                    },
                ],
                rowCallback: function (row, data, index) {

                },
                initComplete: function (settings, json) {

                }
            });

            $('#myModalDetDateMedical').modal('show');
        });

    getData();

    $('.btnSearchAll').on('click', function () {
        date_range = null;
        date_current = '';
        getData();
    });
});