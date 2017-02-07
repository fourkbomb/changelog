function renderChanges(data, textStatus, xhr) {
    var res = data.res;
    for (var el in res) {
        if (!res.hasOwnProperty(el)) {
            continue;
        }
        let date = new Date(res[el].submitted * 1000);
        row = "<tr><td>" + res[el].subject + "</td><td>" + res[el].project + "</td><td>" + date.toLocaleString() + "</td></tr>";
        document.getElementById("change-table").innerHTML += row;
    }
}

$(document).ready(function() {
    $.getJSON('api/v1/changes/all', null, function(data, textStatus, xhr) {
        $('#change-table').html('');
        renderChanges(data, textStatus, xhr);
    });
});

