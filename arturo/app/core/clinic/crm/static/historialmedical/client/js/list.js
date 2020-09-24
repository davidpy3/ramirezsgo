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

    $.ajax({
        url: pathname,
        data: parameters,
        method: 'POST',
        dataType: 'json',
        success: function (request) {
            if (!request.hasOwnProperty('error')) {
                var html = '';
                $.each(request, function (key, item) {
                    html += '<div class="time-label">';
                    html += '<span class="bg-green">' + item.date_joined + '</span>';
                    html += '</div>';

                    html += '<div>';
                    html += '<i class="fas fa-first-aid bg-blue"></i>';
                    html += '<div class="timeline-item">';
                    html += '<span class="time"><i class="fas fa-clock"></i> ' + item.hour + '</span>';
                    html += '<h3 class="timeline-header"><a>' + item.status.name + '</a></h3>';
                    html += '<div class="timeline-body">';
                    html += '<b>Último periodo de regla: </b>' + item.lastperiod_date + '</p>';
                    html += '<p><b>Sintomas: </b>' + item.symptoms + '<br>';
                    html += '<p><b>Diagnóstico: </b>' + item.diagnosis + '<br>';
                    html += '<p><b>Tratamiento: </b>' + item.treatment + '<br>';
                    html += '</div></div></div></div>';
                });

                $('.timeline').html(html);

                return false;
            }
            message_error(request.error);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            message_error(errorThrown + ' ' + textStatus);
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

    getData();

    $('.btnSearchAll').on('click', function () {
        date_range = null;
        date_current = '';
        getData();
    });
});