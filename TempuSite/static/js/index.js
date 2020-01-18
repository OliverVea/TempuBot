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
    let headers = ['date', 'time', 'shorthand']
    
    $('#log_table').html('<tr class=\'header\'><td>Date</td> <td>Time</td> <td>Shorthand</td></tr>')

    status['log'].forEach(entry => {
        let row = '<tr>'
        headers.forEach(key => {
            row += '<td>' + entry[key] + '</td>'
        });
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