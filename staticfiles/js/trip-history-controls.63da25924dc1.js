// JavaScript for filtering trips based on search input
function filterTrips() {
    var input = document.getElementById('search-input').value.trim().toUpperCase();
    var cards = document.querySelectorAll('.card');
    
    cards.forEach(function(card) {
        var fromLocation = card.querySelector('.card-content p:nth-of-type(1)').textContent.trim().toUpperCase();
        var toLocation = card.querySelector('.card-content p:nth-of-type(2)').textContent.trim().toUpperCase();
        
        if (fromLocation.includes(input) || toLocation.includes(input)) {
            card.style.display = 'grid';
        } else {
            card.style.display = 'none';
        }
    });
}

// JavaScript for showing all trips
function showAllTrips() {
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        card.style.display = 'grid';
    });
}

// JavaScript for toggling the visibility of trip details
function toggleDetails(button) {
    var details = button.parentNode.nextElementSibling;
    var isVisible = details.style.display === 'block';

    // Hide all trip details first
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        var cardDetails = card.querySelector('.card-details');
        if (cardDetails) {
            cardDetails.style.display = 'none';
        }
        
        var showMoreButton = card.querySelector('.btn');
        if (showMoreButton) {
            showMoreButton.textContent = 'Show more details';
        }
    });

    // Toggle the selected trip details
    details.style.display = isVisible ? 'none' : 'block';

    // Change button text based on visibility
    button.textContent = isVisible ? 'Show more details' : 'Hide details';
}

