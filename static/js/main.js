String.format = function (string, obj) {
    return string.replace(/{([^}]+)}/g, function(m, thing) {
        return typeof obj[thing] != 'undefined' ? obj[thing] : m
    })
}

FORMAT = `<li class="collection-item flex-row">
    <div class="flex-col">
        <a href="{url}">{subject}</a>
        <span class="project-name">{project}</span>
    </div>
    <div class="flex-col secondary-content">
        <div class="flex-row">
            {images}
        </div>
    </div>
</li>
`;

IMAGE = '<img class="{class}" src="{url}" alt="{label}: {name}" title="{label}: {name}"/>';
function renderChanges(data, textStatus, xhr) {
    var res = data.res;
    for (var el in res) {
        if (!res.hasOwnProperty(el)) {
            continue;
        }
        let date = new Date(res[el].submitted * 1000);
        // get approvers
        let imgs = String.format(IMAGE, {
            'url': res[el].owner.avatars[32],
            'name': res[el].owner.name,
            'label': 'Owner',
            'class': 'owner voter',
        });
        for (let label in res[el].labels) {
            if (res[el].labels[label].approved) {
                imgs += String.format(IMAGE, {
                    'url': res[el].labels[label].approved.avatars[32],
                    'name': res[el].labels[label].approved.name,
                    'label': label,
                    'class': 'voter',
                });
            }
        }
        let args = {
            'url': res[el].url,
            'subject': res[el].subject,
            'project': res[el].project,
            'images': imgs,
        };
        document.getElementById("changes").innerHTML += String.format(FORMAT, args);
    }
    g = res;
}

$(document).ready(function() {
    $.getJSON('/api/v1/changes/' + device + '/', null, function(data, textStatus, xhr) {
        // remove "loading"
        $('#changes .collection-item').remove();
        renderChanges(data, textStatus, xhr);
    });
});

