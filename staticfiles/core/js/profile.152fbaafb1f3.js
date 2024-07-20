// JavaScript to enforce uppercase on license plate number
document.addEventListener('DOMContentLoaded', function() {
    const licensePlateInput = document.querySelector('[data-uppercase="true"]');
    if (licensePlateInput) {
        licensePlateInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }
});

// Custom function to handle file input text change
function updateFileInputLabel() {
    var input = document.getElementById('id_profile_picture');
    var label = document.querySelector('.custom-file-upload');
    if (input.files && input.files.length > 0) {
        label.textContent = input.files[0].name;
    } else {
        label.textContent = 'Choose Profile Picture';
    }
}

// Bind change event listener to file input
document.getElementById('id_profile_picture').addEventListener('change', updateFileInputLabel);
