var tblPurchase;
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

    tblPurchase = $('#data').DataTable({
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
        columns: [
            {data: "id"},
            {data: "provider.name"},
            {data: "provider.ruc"},
            {data: "date_joined"},
            {data: "subtotal"},
            {data: "id"},
        ],
        columnDefs: [
            {
                targets: [-2],
                class: 'text-center',
                render: function (data, type, row) {
                    return '$' + parseFloat(data).toFixed(2);
                }
            },
            {
                targets: [-1],
                class: 'text-center',
                render: function (data, type, row) {
                    var buttons = '';
                    buttons += '<a class="btn btn-info btn-xs btn-flat" data-toggle="tooltip" title="Detalles" rel="det"><i class="fas fa-folder-open"></i></a> ';
                    buttons += '<a href="/clinic/scm/purchase/delete/' + row.id + '/" class="btn btn-danger btn-xs btn-flat" data-toggle="tooltip" title="Eliminar"><i class="fas fa-trash"></i></a> ';
                    return buttons;
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

    $('#data tbody').on('click', 'a[rel="det"]', function () {
        $('.tooltip').remove();
        var tr = tblPurchase.cell($(this).closest('td, li')).index(),
            rows = tblPurchase.row(tr.row).data();
        $('#tblDet').DataTable({
            responsive: true,
            autoWidth: false,
            destroy: true,
            ajax: {
                url: pathname,
                type: 'POST',
                data: {
                    'action': 'search_detproducts',
                    'id': rows.id
                },
                dataSrc: ""
            },
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
                {
                    targets: [-2],
                    class: 'text-center',
                    render: function (data, type, row) {
                        return data;
                    }
                }
            ]
        });
        $('#myModalDet').modal('show');
    });

    getData();

    $('.btnSearchAll').on('click', function () {
        date_range = null;
        date_current = '';
        getData();
    });
});