
        // Add event listener to the button in the hero section
        document.querySelector('#hero button').addEventListener('click', function() {
            // Scroll to the services section
            document.querySelector('#services').scrollIntoView({ behavior: 'smooth' });
        });

        // Add event listener to the form in the contact section
        document.querySelector('#contact form').addEventListener('submit', function(event) {
            // Prevent the default form submission behavior
            event.preventDefault();
            // Get the form data
            var formData = new FormData(this);
            // Send the form data to the server
            fetch('/submit', {
                method: 'POST',
                body: formData
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                console.log(data);
            })
            .catch(function(error) {
                console.error(error);
            });
        });
        