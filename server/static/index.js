var poly;
var map;
var geocoder;
var infowindow;
var markers = [];

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

function postJSON(url, data, success, error)
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
	    var data = {
		'code': code, 'name': initials,
		'lat': results[0].geometry.location.lat(),
		'lng': results[0].geometry.location.lng(),
	    };
	    postJSON('/new_node', data,
		     function(resp) {
			 data = JSON.parse(resp);
			 initPage();
			 map.setCenter(results[0].geometry.location);
			 displayCode(data.message, data.next_code);
		     },
		     function(xhr) {
			 alert("Invalid code. Please try again.");
		     }
		    );
	} else {
	    alert('Invalid location. Please try again.');
	}
    });
}

function hideForm() {
    document.body.style.overflow = "visible";

    var modal = M.Modal.getInstance(document.getElementById("node-form"));
    modal.close();
}

function displayCode(message, code) {
    var c = document.getElementById("codeCanvas");
    var ctx = c.getContext("2d");

    var qr = new QRious({
	value: window.location.host+'/#'+code,
	background: 'white', // background color
	foreground: 'black', // foreground color
	level: 'L', // Error correction level of the QR code (L, M, Q, H)
	mime: 'image/png', // MIME type used to render the image for the QR code
	size: 300 // Size of the QR code in pixels.
    });
    qrcode = new Image();
    qrcode.src = qr.toDataURL();
    qrcode.onload = function() {
	ctx.drawImage(qrcode,c.width-350,c.height-350);

	var button = document.getElementById('btn-download');
	var dataURL = c.toDataURL("image/png");
	button.href = dataURL;
    };

    ctx.fillStyle = 'white';
    ctx.fillRect(0,0,c.width,c.height);

    ctx.font = "50px Arial";
    ctx.fillStyle = 'black';
    ctx.fillText(message, 20, 60);

    ctx.font = "30px Arial"
    ctx.fillText("Add your compliment to the map at", 20, 110);
    ctx.fillText(window.location.host, 20, 145);
    ctx.fillText("with code:", 20, 180);
    ctx.font = "30px Arial";
    ctx.fillText(code, 30, 220);

    ctx.fillText("Or, scan this QR code:", 20, c.height-300);
    var modal = M.Modal.getInstance(document.getElementById("code-display"));
    modal.open();
}

function initPage() {
    if(window.location.hash.split('#')[1]) {
	document.getElementById('code').value = window.location.hash.split('#')[1]
    }

    var elem = document.querySelector('.fixed-action-btn');
    var instance = M.FloatingActionButton.init(elem);

    var elem = document.querySelector('#code-display');
    var instance = M.Modal.init(elem);

    var elem = document.querySelector('#node-form');
    var instance = M.Modal.init(elem);

    markers = [];

    map = new google.maps.Map(document.getElementById('map'), {
	zoom: 4,
	center: {lat: 39.8283, lng: -78.57950},
	disableDefaultUI: true,
	zoomControl: true,
	styles: mapStyle
    });

    geocoder = new google.maps.Geocoder();

    document.getElementById('submit').addEventListener('click', function() {
	hideForm();
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

	    infowindow = new google.maps.InfoWindow();
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
		    title: paths[p].message + " - " + node.person +
			" - " + node.time_created+"-0000",
		    map: map,
		    clickable: true
		});
		marker.content = '<div id="bodyContent">'+
		    '<p>' +  paths[p].message + '<br>' + node.person +
		    '<br>' + new Date(node.time_created+"-0000").toLocaleString() + '</p>' + '</div>';
		google.maps.event.addListener(marker, 'click', function() {
		    infowindow.setContent(this.content)
		    infowindow.open(map, this);
		});
		markers.push(marker);
	    }
	    var markerCluster = new MarkerClusterer(map, markers, {imagePath:'/static/clusters/m'})
	}
    });
}
