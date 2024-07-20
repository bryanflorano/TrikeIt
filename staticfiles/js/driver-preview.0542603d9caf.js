function driverPreviewRoute(button, bookingId, pickupLat, pickupLng, dropoffLat, dropoffLng) {
    var routeMapContainer = document.getElementById('route-map-' + bookingId);

    if (routeMapContainer.style.display === 'block') {
        routeMapContainer.style.display = 'none';
        button.textContent = 'Preview Route';
    } else {
        routeMapContainer.style.display = 'block';
        button.textContent = 'Close Preview';

        var pickupLatLng = { lat: pickupLat, lng: pickupLng };
        var dropoffLatLng = { lat: dropoffLat, lng: dropoffLng };

        var map = new google.maps.Map(document.getElementById('map-' + bookingId), {
            center: pickupLatLng,
            zoom: 14
        });

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

        var directionsService = new google.maps.DirectionsService();
        var directionsRenderer = new google.maps.DirectionsRenderer({
            map: map,
            suppressMarkers: true
        });

        var request = {
            origin: pickupLatLng,
            destination: dropoffLatLng,
            travelMode: 'DRIVING'
        };

        directionsService.route(request, function(response, status) {
            if (status === 'OK') {
                directionsRenderer.setDirections(response);

                var route = response.routes[0];
                var distance = route.legs[0].distance.text;
                var estimated_duration = route.legs[0].duration.text;

                document.getElementById('distance-' + bookingId).textContent = 'Distance: ' + distance;
                document.getElementById('estimated_duration-' + bookingId).textContent = 'Estimated duration: ' + estimated_duration;
            } else {
                window.alert('Directions request failed due to ' + status);
            }
        });
    }
}
