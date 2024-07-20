// Initialize map with directions service and renderer
function initializeMap() {
    var map;
    var directionsService = new google.maps.DirectionsService();
    var directionsRenderer = new google.maps.DirectionsRenderer();

    // Get pickup and dropoff locations from confirmed booking data
    var pickupLocation = new google.maps.LatLng({{ confirmed_booking.pickup_lat }}, {{ confirmed_booking.pickup_lng }});
    var dropoffLocation = new google.maps.LatLng({{ confirmed_booking.dropoff_lat }}, {{ confirmed_booking.dropoff_lng }});

    // Set map options
    var mapOptions = {
        center: pickupLocation, // Center map on pickup location
        zoom: 17 // Zoom level
    };

    // Create map and bind directions renderer
    map = new google.maps.Map(document.getElementById('map'), mapOptions);
    directionsRenderer.setMap(map);

    // Add marker based on booking status
    {% if profile.is_passenger %}
        {% if confirmed_booking.status == 'enroute_to_dest' %}
            // Add marker at dropoff location for passengers
            new google.maps.Marker({
                position: dropoffLocation,
                map: map,
                title: 'Drop-off Location'
            });
            map.setCenter(dropoffLocation); // Center map on dropoff location
        {% else %}
            // Add marker at pickup location for passengers
            new google.maps.Marker({
                position: pickupLocation,
                map: map,
                title: 'Pick-up Location'
            });
            map.setCenter(pickupLocation); // Center map on pickup location
        {% endif %}
    {% elif profile.is_driver %}
        {% if confirmed_booking.status == 'enroute_to_dest' %}
            // Add marker at dropoff location for drivers
            new google.maps.Marker({
                position: dropoffLocation,
                map: map,
                title: 'Drop-off Location'
            });
            map.setCenter(dropoffLocation); // Center map on dropoff location
        {% else %}
            // Add marker at pickup location for drivers
            new google.maps.Marker({
                position: pickupLocation,
                map: map,
                title: 'Pick-up Location'
            });
            map.setCenter(pickupLocation); // Center map on pickup location
        {% endif %}
    {% endif %}
}
