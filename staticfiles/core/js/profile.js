// JavaScript to enforce uppercase on license plate number
document.addEventListener('DOMContentLoaded', function() {
    const licensePlateInput = document.querySelector('[data-uppercase="true"]');
    if (licensePlateInput) {
        licensePlateInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
});
