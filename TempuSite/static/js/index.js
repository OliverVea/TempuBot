$(document).ready(function() {
    refresh_data()
    setInterval(refresh_data, 3000)
});

function refresh_data() {
    $.ajax({
        type: "GET",
        url: "/status",
        contentType: "charset=UTF-16LE",
        success: function(str) {
            json = JSON.parse(str)
            update_status(json)
            update_table(json)
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr, textStatus, errorThrown)
        }
    });
}

function update_table(status) {
    $('#log_table > tbody').children().not(':first').remove();

    status['log'].forEach(entry => {
        let row = '<tr>'
        row += '<td>' + entry.date + '</td>'
        row += '<td>' + entry.time + '</td>'
        row += '<td>' + entry.type + '</td>'
        row += '<td>' + entry.shorthand + '</td>'
        row += '</tr>'
        $('#log_table').append(row)
    });
}

function update_status(status) {
    console.log(status)

    $('#childstatus').html(status['children'])

    if (status['alive']) {
        $('#processstatus').removeClass('negative neutral').addClass('positive').html("ALIVE")

        $('#memorystatus').html(status['memory']['use'] + status['memory']['unit'])
    }
    else {
        $('#processstatus').removeClass('neutral positive').addClass('negative').html("DEAD")
    } 


}