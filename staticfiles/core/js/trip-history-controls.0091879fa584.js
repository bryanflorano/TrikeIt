// JavaScript for filtering trips based on search input
function filterTrips() {
    var input = document.getElementById('search-input').value.toUpperCase();
    var trips = document.querySelectorAll('.trip');
    
    trips.forEach(function(trip) {
        var fromLocation = trip.querySelector('.trip-summary div:nth-child(2)').textContent.toUpperCase();
        var toLocation = trip.querySelector('.trip-summary div:nth-child(3)').textContent.toUpperCase();
        
        if (fromLocation.includes(input) || toLocation.includes(input)) {
            trip.style.display = 'block';
        } else {
            trip.style.display = 'none';
        }
    });
}

// JavaScript for showing all trips
function showAllTrips() {
    var trips = document.querySelectorAll('.trip');
    trips.forEach(function(trip) {
        trip.style.display = 'block';
    });
}

// JavaScript for toggling the visibility of trip details
function toggleDetails(button) {
    var details = button.parentNode.nextElementSibling;
    var isVisible = details.style.display === 'block';

    // Hide all trip details first
    var allDetails = document.querySelectorAll('.trip-details');
    allDetails.forEach(function(item) {
        item.style.display = 'none';
    });

    // Toggle the selected trip details
    details.style.display = isVisible ? 'none' : 'block';

    // Update all "Show more details" buttons
    var allButtons = document.querySelectorAll('.toggle-button');
    allButtons.forEach(function(btn) {
        btn.textContent = 'Show more details';
    });

    // Change button text based on visibility
    button.textContent = isVisible ? 'Show more details' : 'Hide details';
}

