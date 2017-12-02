// Google Map
let map;

// Markers for map
let markers = [];
let connectingmarkers = [];


let connectionmode = false;

// Info window
let info = new google.maps.InfoWindow();


// Execute when the DOM is fully loaded
$(document).ready(function() {

    document.getElementById("removeconnections").style.visibility = "hidden"

    // Styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    let styles = [

        // Hide Google's labels
        {
            featureType: "all",
            elementType: "labels",
            stylers: [{
                visibility: "off"
            }]
        },

        // Hide roads
        {
            featureType: "road",
            elementType: "geometry",
            stylers: [{
                visibility: "off"
            }]
        }

    ];

    // Options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    let options = {
        center: { // Cambridge, MA
            lat: 42.3770,
            lng: -71.1256

        },
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 14,
        panControl: true,
        styles: styles,
        zoom: 11,
        zoomControl: true
    };


    // Get DOM node in which map will be instantiated
    let canvas = $("#map-canvas").get(0);

    // Instantiate map
    map = new google.maps.Map(canvas, options);

    // Configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);

});


// Add marker for place to map
function addMarker(place) {

    //Declare and add a new marker
    var marker = new google.maps.Marker({
        position: {
            lat: parseFloat(place.Latitude_Val),
            lng: parseFloat(place.Longitude_Val)

        },
        map: map,
        labelOrigin: new google.maps.Point(16, 64),
        label: {
            text: place.IATA_Code

        }

    });


    //Listener that wait for the marker to be clicked
    marker.addListener('click', function() {

        info.setContent("Loading..."); //Temp message until the rest loads


        var contentString = '<b>' + place.Airport_Name + '</b>';
        contentString = contentString + '<br><b>IATA Code:</b> ' + place.IATA_Code + '';
        contentString = contentString + '<br><b>Serves:</b> ' + place.Serves + '';
        contentString = contentString + '<br><b>Location:</b> ' + place.Location + '';
        info.setContent(contentString);

        info.open(map, marker);

        if (connectionmode == false) {
            showroutes(place);
        }
    });

    markers.push(marker);
    marker.setMap(map);
}



//Show all connecting airports from selected airport
function showroutes(place) {

    connectionmode = true;

    let parameters = {
        id: place.id,
        star: document.getElementById("star").checked,
        ow: document.getElementById("ow").checked,
        sky: document.getElementById("sky").checked
    };
    $.getJSON("/routesearch", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        removeMarkers();

        addMarker(place);
        // Add connecting markers to map
        for (let i = 0; i < data.length; i++) {
            addConnectingMarker(data[i]);
        }

        if (map.zoom > 5) {
            map.setZoom(5);
        }
        document.getElementById("removeconnections").style.visibility = "visible"
    });

}


// Add marker for place to map
function addConnectingMarker(place) {

    console.log("adding a connecting marker")
    //Declare and add a new marker
    var connectingmarker = new google.maps.Marker({
        position: {
            lat: parseFloat(place.latitude_val),
            lng: parseFloat(place.longitude_val)

        },
        map: map,
        icon: 'http://maps.google.com/mapfiles/ms/micons/plane.png',
        labelOrigin: new google.maps.Point(16, 64),
        label: {
            text: place.connairportiata

        }

    });


    //Listener that wait for the marker to be clicked
    connectingmarker.addListener('click', function() {

        info.setContent("Loading..."); //Temp message until the rest loads

        var e = document.getElementById("directionality");
        var directionalitystring = e.options[e.selectedIndex].text;

        var f = document.getElementById("class");
        var classstring = f.options[f.selectedIndex].text;

        var contentString = '<b>' + place.airport_name + '</b>';
        contentString = contentString + '<br><b>IATA Code:</b> ' + place.connairportiata + '';
        contentString = contentString + '<br><b>Serves:</b> ' + place.serves + '';
        contentString = contentString + '<br><b>Location:</b> ' + place.location + '';
        contentString = contentString + '<br>';
        contentString = contentString + '<br><b>Connecting Airlines:</b>';

        let parameters = {
            airport1: place.originairportid,
            airport2: place.connairportid,
            star: document.getElementById("star").checked,
            ow: document.getElementById("ow").checked,
            sky: document.getElementById("sky").checked
        };
        $.getJSON("/connectingairlines", parameters, function(data, textStatus, jqXHR) {

            console.log('Before' + contentString);

            // Add connecting markers to map
            for (let i = 0; i < data.length; i++) {
                contentString = contentString + '<br><a class="nav-link" href="/calcmiles?airportid1=' + place.originairportid + '&airportid2=' + place.connairportid + '&airlineid=' + data[i].airlineid + '&directionality=' + directionalitystring + '&travelclass=' + classstring + '&traveldate=' + document.getElementById("traveldate").value + '" target="_blank">' + data[i].airline_brand + ' (' + data[i].iata_designator + ')</a>';
                //contentString = contentString + '<br><a class="nav-link" href="/calcmiles?airportid1=' + place.originairportid + '&airportid2=' + place.connairportid + '&airlineid=' + data[i].airlineid + '" target="_blank">' + data[i].airline_brand + ' (' + data[i].iata_designator + ')</a>';
            }


            contentString = contentString + '<br><br>';
            contentString = contentString + '<i>Click on airlines above to see mileage requirements</i>';

            console.log("After" + contentString);

            info.setContent(contentString);
        });



        info.open(map, connectingmarker);

        showroutes(place);
    });

    connectingmarkers.push(connectingmarker);
    connectingmarker.setMap(map);
}


//Remove all connections
function clearconnections() {

    //Loop through the markers and unload them
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }

    //Empty the array
    markers = [];

    //Loop through the connecting markers and unload them
    for (let i = 0; i < connectingmarkers.length; i++) {
        connectingmarkers[i].setMap(null);
    }

    //Empty the array
    connectingmarkers = [];

    connectionmode = false;
    document.getElementById("removeconnections").style.visibility = "hidden"

    update();
}


// Configure application
function configure() {
    // Update UI after map has been dragged
    google.maps.event.addListener(map, "dragend", function() {

        // If info window isn't open
        // http://stackoverflow.com/a/12410385
        if (!info.getMap || !info.getMap()) {
            update();
        }
    });

    // Update UI after zoom level changes
    google.maps.event.addListener(map, "zoom_changed", function() {
        update();
    });

    // Configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    }, {
        display: function(suggestion) {
            return null;

        },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>{{IATA_Code}} - {{Serves}} ({{Airport_Name}})</div>"
                // place.IATA_Code + ' - ' + place.Serves + '(' + place.Airport_Name + ')'

            )
        }
    });

    // Re-center map after place is selected from drop-down
    $("#q").on("typeahead:selected", function(eventObject, suggestion, name) {

        // Set map's center
        map.setCenter({
            lat: parseFloat(suggestion.Latitude_Val),
            lng: parseFloat(suggestion.Longitude_Val)

        });

        // Update UI
        update();
    });

    // Hide info window when text box has focus
    $("#q").focus(function(eventData) {
        info.close();
    });

    // Re-enable ctrl- and right-clicking (and thus Inspect Element) on Google Map
    // https://chrome.google.com/webstore/detail/allow-right-click/hompjdfbfmmmgflfjdlnkohcplmboaeo?hl=en
    document.addEventListener("contextmenu", function(event) {
        event.returnValue = true;
        event.stopPropagation && event.stopPropagation();
        event.cancelBubble && event.cancelBubble();
    }, true);

    // Update UI
    update();

    // Give focus to text box
    $("#q").focus();
}


// Remove markers from map
function removeMarkers() {
    //Loop through the markers and unload them
    for (let i = 0; i < markers.length; i++) {
        markers[i].setMap(null);
    }

    //Empty the array
    markers = []
}


// Search database for typeahead's suggestions
function search(query, syncResults, asyncResults) {
    // Get places matching query (asynchronously)
    let parameters = {
        q: query
    };
    $.getJSON("/search", parameters, function(data, textStatus, jqXHR) {

        // Call typeahead's callback with search results (i.e., places)
        asyncResults(data);

        map.setZoom(11);
    });
}


// Show info window at marker with content
function showInfo(marker, content) {
    // Start div
    let div = "<div id='info'>";
    if (typeof(content) == "undefined") {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    } else {
        div += content;
    }

    // End div
    div += "</div>";

    // Set info window's content
    info.setContent(div);

    // Open info window (if not already open)
    info.open(map, marker);
}


// Update UI's markers
function update() {

    if (connectionmode == false) {
        // Get map's bounds
        let bounds = map.getBounds();
        let ne = bounds.getNorthEast();
        let sw = bounds.getSouthWest();

        // Get places within bounds (asynchronously)
        let parameters = {
            ne: `${ne.lat()},${ne.lng()}`,
            q: $("#q").val(),
            sw: `${sw.lat()},${sw.lng()}`
        };
        $.getJSON("/update", parameters, function(data, textStatus, jqXHR) {

            // Remove old markers from map
            removeMarkers();

            // Add new markers to map
            for (let i = 0; i < data.length; i++) {
                addMarker(data[i]);
            }
        });
    };
}