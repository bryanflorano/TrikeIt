function initMap(pickupLat, pickupLng, dropoffLat, dropoffLng) {
    // Define pickup and dropoff locations as LatLng objects
    var pickupLatLng = { lat: pickupLat, lng: pickupLng };
    var dropoffLatLng = { lat: dropoffLat, lng: dropoffLng };

    // Initialize Google Maps with the pickup location as center
    var map = new google.maps.Map(document.getElementById('map'), {
        center: pickupLatLng,
        zoom: 14
    });

    // Add markers for pickup and dropoff locations on the map
    var pickupMarker = new google.maps.Marker({
        position: pickupLatLng,
        map: map,
        title: 'Pick-up Location'
    });

    var dropoffMarker = new google.maps.Marker({
        position: dropoffLatLng,
        map: map,
        title: 'Drop-off Location'
    });

    // Initialize DirectionsService and DirectionsRenderer
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true  // Do not display default markers
    });

    // Define request object for directions
    var request = {
        origin: pickupLatLng,
        destination: dropoffLatLng,
        travelMode: 'DRIVING'
    };

    // Make a directions request
    directionsService.route(request, function(response, status) {
        if (status === 'OK') {
            // Display the route on the map
            directionsRenderer.setDirections(response);

            // Extract route details like distance and estimated duration
            var route = response.routes[0];
            var distance = route.legs[0].distance.text;
            var estimated_duration = route.legs[0].duration.text;

            // Display route details on the page
            document.getElementById('distance').textContent = 'Distance: ' + distance;
            document.getElementById('estimated_duration').textContent = 'Estimated duration: ' + estimated_duration;
        } else {
            // Handle errors if directions request fails
            window.alert('Directions request failed due to ' + status);
        }
    });
}