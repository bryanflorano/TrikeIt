var pickupMarker;
var dropoffMarker;
var map;
var directionsService;
var directionsRenderer;
var activePickupLocation;
var activeDropoffLocation;

function initMap(pickupLat, pickupLng, dropoffLat, dropoffLng) {
    var mapCenter = { lat: 14.639898, lng: 121.078195 }; // Default center coordinates (e.g., Manila)

    map = new google.maps.Map(document.getElementById('map'), {
        center: mapCenter,
        zoom: 15
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true
    });

    // Initialize Autocomplete for pickup_location field
    var pickupInput = document.getElementById('pickup_location');
    var pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput, {
        componentRestrictions: { country: 'ph' }
    });

    // Initialize Autocomplete for dropoff_location field
    var dropoffInput = document.getElementById('dropoff_location');
    var dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput, {
        componentRestrictions: { country: 'ph' }
    });

    // Event listener for pickup location autocomplete
    pickupAutocomplete.addListener('place_changed', function() {
        var place = pickupAutocomplete.getPlace();
        if (!place.geometry) {
            console.error('Autocomplete returned place contains no geometry');
            return;
        }
        updateMap(place.geometry.location, 'pickup', place.formatted_address);
        checkRouteLocations(); // Call checkRouteLocations after updating dropoff location
    });

    // Event listener for dropoff location autocomplete
    dropoffAutocomplete.addListener('place_changed', function() {
        var place = dropoffAutocomplete.getPlace();
        if (!place.geometry) {
            console.error('Autocomplete returned place contains no geometry');
            return;
        }
        updateMap(place.geometry.location, 'dropoff', place.formatted_address);
        checkRouteLocations(); // Call checkRouteLocations after updating pickup location
    });

    // Click event listener on the map to set pickup and dropoff locations manually
    google.maps.event.addListener(map, 'click', function(event) {
        var clickedLocation = event.latLng;

        // Reverse geocode the clicked location to get address
        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({ 'location': clickedLocation }, function(results, status) {
            if (status === 'OK') {
                if (!pickupMarker) {
                    // If no pickup marker exists, set pickup marker and update field
                    pickupMarker = new google.maps.Marker({
                        position: clickedLocation,
                        map: map,
                        title: 'Pick-up Location'
                    });
                    document.getElementById('pickup_location').value = results[0].formatted_address;
                    checkRouteLocations(); // Call checkRouteLocations after setting markers
                } else if (!dropoffMarker) {
                    // If pickup marker exists but no dropoff marker, set dropoff marker and update field
                    dropoffMarker = new google.maps.Marker({
                        position: clickedLocation,
                        map: map,
                        title: 'Drop-off Location'
                    });
                    document.getElementById('dropoff_location').value = results[0].formatted_address;
                    calculateAndDisplayRoute(pickupMarker.getPosition(), dropoffMarker.getPosition());
                } else {
                    // Clear existing markers and set new pickup marker
                    pickupMarker.setMap(null);
                    dropoffMarker.setMap(null);
                    pickupMarker = new google.maps.Marker({
                        position: clickedLocation,
                        map: map,
                        title: 'Pick-up Location'
                    });
                    dropoffMarker = null; // Reset dropoff marker
                    document.getElementById('pickup_location').value = results[0].formatted_address;
                    document.getElementById('dropoff_location').value = '';
                }
            } else {
                console.error('Geocoder failed due to: ' + status);
            }
            checkRouteLocations();
        });
    });

    // If active_route is available, initialize map with stored data
    if (pickupLat && pickupLng && dropoffLat && dropoffLng) {
        var pickupLocation = new google.maps.LatLng(pickupLat, pickupLng);
        var dropoffLocation = new google.maps.LatLng(dropoffLat, dropoffLng);

        pickupMarker = new google.maps.Marker({
            position: pickupLocation,
            map: map,
            title: 'Pick-up Location'
        });

        dropoffMarker = new google.maps.Marker({
            position: dropoffLocation,
            map: map,
            title: 'Drop-off Location'
        });

        calculateAndDisplayRoute(pickupLocation, dropoffLocation);
        checkRouteLocations();
    }
}

function updateMap(location, type, formattedAddress) {
    if (type === 'pickup') {
        // Clear existing pickup marker if it exists
        if (pickupMarker) {
            pickupMarker.setMap(null);
        }
        // Set new pickup marker
        pickupMarker = new google.maps.Marker({
            position: location,
            map: map,
            title: 'Pick-up Location'
        });
        map.setCenter(location); // Center map on the new pickup location

        // Optionally, update any other map-related functionality here
    } else if (type === 'dropoff') {
        // Clear existing dropoff marker if it exists
        if (dropoffMarker) {
            dropoffMarker.setMap(null);
        }
        // Set new dropoff marker
        dropoffMarker = new google.maps.Marker({
            position: location,
            map: map,
            title: 'Drop-off Location'
        });
        map.setCenter(location); // Center map on the new dropoff location

        // Optionally, update any other map-related functionality here
    }

    // Calculate and display route if both pickup and dropoff markers are set
    if (pickupMarker && dropoffMarker) {
        calculateAndDisplayRoute(pickupMarker.getPosition(), dropoffMarker.getPosition());
    }
    checkRouteLocations();
}

function calculateAndDisplayRoute(origin, destination) {
    var request = {
        origin: origin,
        destination: destination,
        travelMode: 'DRIVING'
    };

    directionsService.route(request, function(response, status) {
        if (status === 'OK') {
            directionsRenderer.setDirections(response);

            var route = response.routes[0];
            var distance = route.legs[0].distance.text;
            var distance_value = route.legs[0].distance.value; // Distance in meters
            var estimated_duration = route.legs[0].duration.text;

            // Populate hidden form fields with route data
            document.getElementById('distance_value').value = distance_value;
            document.getElementById('distance').value = distance;
            document.getElementById('estimated_duration').value = estimated_duration;

            // Update HTML elements with route details
            document.getElementById('distance-in-html').textContent = 'Distance: ' + distance;
            document.getElementById('estimated-duration-in-html').textContent = 'Estimated Duration: ' + estimated_duration;

            checkRouteLocations();
        } else {
            window.alert('Directions request failed due to ' + status);
        }
    });
}

// Function to check if pickup and dropoff locations match active locations
function checkRouteLocations() {
    var pickupInputValue = document.getElementById('pickup_location').value.trim();
    var dropoffInputValue = document.getElementById('dropoff_location').value.trim();

    var pickupLocationMatch = (activePickupLocation === pickupInputValue);
    var dropoffLocationMatch = (activeDropoffLocation === dropoffInputValue);

    var paymentButton = document.getElementById('proceed_payment');
    if (pickupLocationMatch && dropoffLocationMatch) {
        paymentButton.disabled = false;
    } else {
        paymentButton.disabled = true;
    }
}
