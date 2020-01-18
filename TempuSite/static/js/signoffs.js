var signoffs

function get_signoffs() {
    $.ajax({
        type: "GET",
        url: "/signofffile",
        contentType: "charset=UTF-16LE",
        success: function(str) {
            signoffs = JSON.parse(str)

            update_table(signoffs)
        },
        error: function (xhr, textStatus, errorThrown) {
            console.log(xhr, textStatus, errorThrown)
        }
    });
}

function capitalize(s) {
    if (typeof s !== 'string') return ''
    return s.charAt(0).toUpperCase() + s.slice(1)
}

function dateString(date) {
    return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

function update_table(signoffs) {
    console.log($('#table_signoff > tbody').children())
    $('#table_signoff > tbody').children().not(':first').remove();

    let i = 0

    signoffs.forEach(signoff => {
        name = capitalize(signoff.name)
        dateStart = new Date(signoff.start)
        dateEnd = new Date(signoff.end)

        console.log(dateStart, dateStart.toString())

        $('#table_signoff').append(`<tr><td>${name}</td><td>${dateString(dateStart)}</td><td>${dateString(dateEnd)}</td><td>${signoff.reason}</td><td onclick='delete_signoff(${i})' class='delete'>x</td></tr>`)
        i++
    });
}

function delete_signoff(i) {
    signoff = signoffs[i]
    
    name = capitalize(signoff.name)
    dateStart = new Date(signoff.start)
    dateEnd = new Date(signoff.end)

    if (!confirm(`Are you sure you want to delete the sign off by ${name} from the ${dateString(dateStart)} to the ${dateString(dateEnd)}. Reason: '${signoff.reason}'?`)) return;

    let message = {type: 'delete', index: i, signoff:signoffs[i]}

    $.ajax({
        url: '/signofffile',
        type: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(message),
        success: function(data) {
            get_signoffs()
        }
    });
}  

$(document).ready(function() {
    get_signoffs()
});