var date_range;
var current_date;
var tblReport;
var columns = [];

function initTable() {
    tblReport = $('#tblReport').DataTable({
        responsive: true,
        autoWidth: false,
        destroy: true,
    });

    $.each(tblReport.settings()[0].aoColumns, function (key, value) {
        columns.push(value.sWidthOrig);
    });
}

function generateReport() {
    var parameters = {
        'action': 'search_report',
        'start_date': current_date,
        'end_date': current_date
    };

    if (date_range != null) {
        parameters['start_date'] = date_range.startDate.format('YYYY-MM-DD');
        parameters['end_date'] = date_range.endDate.format('YYYY-MM-DD');
    }

    tblReport = $('#tblReport').DataTable({
        destroy: true,
        responsive: true,
        autoWidth: false,
        select: true,
        ajax: {
            url: pathname,
            type: 'POST',
            data: parameters,
            dataSrc: ''
        },
        order: [[0, 'asc']],
        paging: false,
        ordering: true,
        searching: false,
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excelHtml5',
                text: 'Descargar Excel <i class="fas fa-file-excel"></i>',
                titleAttr: 'Excel',
                className: 'btn btn-success btn-flat btn-xs'
            },
            {
                extend: 'pdfHtml5',
                text: 'Descargar Pdf <i class="fas fa-file-pdf"></i>',
                titleAttr: 'PDF',
                className: 'btn btn-danger btn-flat btn-xs',
                download: 'open',
                orientation: 'landscape',
                pageSize: 'LEGAL',
                customize: function (doc) {
                    doc.styles = {
                        header: {
                            fontSize: 18,
                            bold: true,
                            alignment: 'center'
                        },
                        subheader: {
                            fontSize: 13,
                            bold: true
                        },
                        quote: {
                            italics: true
                        },
                        small: {
                            fontSize: 8
                        },
                        tableHeader: {
                            bold: true,
                            fontSize: 11,
                            color: 'white',
                            fillColor: '#2d4154',
                            alignment: 'center'
                        }
                    };
                    doc.content[1].table.widths = columns;
                    doc.content[1].margin = [0, 35, 0, 0];
                    doc.content[1].layout = {};
                    doc['footer'] = (function (page, pages) {
                        return {
                            columns: [
                                {
                                    alignment: 'left',
                                    text: ['Fecha de creación: ', {text: current_date}]
                                },
                                {
                                    alignment: 'right',
                                    text: ['página ', {text: page.toString()}, ' de ', {text: pages.toString()}]
                                }
                            ],
                            margin: 20
                        }
                    });

                }
            }
        ],
        columns: [
            {data: "id"},
            {data: "client.full_name"},
            {data: "date_joined"},
            {data: "hour"},
            {data: "status.name"},
        ],
        columnDefs: [
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    return data;
                }
            }
        ],
        rowCallback: function (row, data, index) {

        },
        initComplete: function (settings, json) {

        },
    });
}

$(function () {

    current_date = new moment().format('YYYY-MM-DD');

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
            generateReport();
        });

    initTable();

    tblReport.on('select', function (e, dt, type, indexes) {
        var data = tblReport.rows(indexes).data().toArray()[0];
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



});