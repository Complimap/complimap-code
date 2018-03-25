var poly;
var map;
var geocoder;

function loadJSON(path, success, error)
{
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                if (success)
                    success(JSON.parse(xhr.responseText));
            } else {
                if (error)
                    error(xhr);
            }
        }
    };
    xhr.open("GET", path, true);
    xhr.send();
}

functionfunction postJSON(url, data, success, error)
{
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-type", "application/json");
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                if (success)
                    success(xhr.responseText);
            } else {
                if (error)
                    error(xhr);
            }
        }
    };
    var data = JSON.stringify(data);
    xhr.send(data);
}

function addNode(resultsMap) {
    var code = document.getElementById('code').value;
    var initials = document.getElementById('initials').value;
    var address = document.getElementById('address').value;
    geocoder.geocode({'address': address}, function(results, status) {
        if (status === 'OK') {
            console.log(results[0].geometry.location);
            var data = {
                'code': code, 'name': initials,
                'lat': results[0].geometry.location.lat(),
                'lng': results[0].geometry.location.lng(),
            };
            postJSON('/new_node', data,
                     function(resp) {
                         displayCode(resp);
                         initMap();
                     },
                     function(xhr) {
                         alert("Invalid code. Please try again.");
                     }
                    );
        } else {
            alert('Geocode was not successful for the following reason: ' + status);
        }
    });
}

function displayCode(code) {
    var c = document.getElementById("codeCanvas");
    var ctx = c.getContext("2d");

    ctx.font = "30px Arial";
    ctx.fillText(code, 10, 50);
    var cd = document.getElementById("code-display");
    cd.style.display = "block";

    var fp = document.getElementById("floating-panel");
    fp.style.display = "none";
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 3,
        center: {lat: 0, lng: 0}
    });

    geocoder = new google.maps.Geocoder();

    document.getElementById('submit').addEventListener('click', function() {
        addNode(map);
    });


    loadJSON('/paths/all', function(paths) {
        for(const p in paths) {
            poly = new google.maps.Polyline({
                strokeColor: '#000000',
                strokeOpacity: 1.0,
                strokeWeight: 2
            });
            poly.setMap(map);

            for(const n in paths[p].nodes) {
                var node = paths[p].nodes[n]
                var path = poly.getPath();
                var loc = new google.maps.LatLng(node.lat, node.lng);

                // Because path is an MVCArray, we can simply append a new coordinate
                // and it will automatically appear.
                path.push(loc);

                // Add a new marker at the new plotted point on the polyline.
                var marker = new google.maps.Marker({
                    position: loc,
                    title: paths[p].message + " - " + node.person + " - " + node.time_created,
                    map: map
                });
            }
        }
    });
}
