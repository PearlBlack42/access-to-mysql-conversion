// AJAX form submission and dynamic form loading

document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form.ajax-form');
    if (!forms.length) return;

    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const url = form.action;
            const method = form.method.toUpperCase();
            const formData = new FormData(form);

            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Form submitted successfully!');
                    // Optionally reset form or redirect
                    form.reset();
                } else if (data.error) {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('There was a problem submitting the form: ' + error.message);
            });
        });
    });
});
