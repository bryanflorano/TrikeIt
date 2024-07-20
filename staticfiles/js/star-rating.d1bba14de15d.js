document.addEventListener('DOMContentLoaded', (event) => {
    const ratingInputs = document.querySelectorAll('.star-rating input[type="radio"]');
    ratingInputs.forEach((input) => {
        input.addEventListener('change', (event) => {
            const selectedRating = event.target.value;
            console.log(`Selected rating: ${selectedRating}`);
        });
    });
});

// Function to validate if a rating is selected
function validateRating() {
    if (!document.querySelector('input[name="rating"]:checked')) {
        document.querySelector('.rating-required-message').style.display = 'block';
        return false; // Prevent form submission
    } else {
        document.querySelector('.rating-required-message').style.display = 'none';
        return true; // Allow form submission
    }
}