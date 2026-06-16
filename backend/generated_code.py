# Import necessary libraries
import http.server
import socketserver
import webbrowser
import os

# Create a simple HTTP server to serve our website
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            # Try to serve the requested file
            http.server.SimpleHTTPRequestHandler.do_GET(self)
        except Exception as e:
            # If the file is not found, serve the index.html
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())

# Create the HTML, CSS, and JavaScript files
def create_website():
    # Create the HTML file
    with open('index.html', 'w') as file:
        file.write('''
        <!-- AI Founders Hub Website -->
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Founders Hub</title>
            <link rel="stylesheet" href="style.css">
        </head>
        <body>
            <!-- Hero Section -->
            <section id="hero">
                <h1>Welcome to AI Founders Hub</h1>
                <p>We provide AI consulting services to help your business thrive</p>
                <button>Learn More</button>
            </section>
            <!-- Services Section -->
            <section id="services">
                <h2>Our Services</h2>
                <div class="service">
                    <h3>AI Strategy</h3>
                    <p>We help you develop a comprehensive AI strategy for your business</p>
                </div>
                <div class="service">
                    <h3>Machine Learning</h3>
                    <p>We provide machine learning solutions to improve your business operations</p>
                </div>
                <div class="service">
                    <h3>Natural Language Processing</h3>
                    <p>We help you develop NLP solutions to improve customer engagement</p>
                </div>
                <div class="service">
                    <h3>Computer Vision</h3>
                    <p>We provide computer vision solutions to improve your business operations</p>
                </div>
            </section>
            <!-- Testimonials Section -->
            <section id="testimonials">
                <h2>What Our Clients Say</h2>
                <div class="testimonial">
                    <p>AI Founders Hub has been instrumental in helping us develop our AI strategy</p>
                    <p>- John Doe, CEO of XYZ Corporation</p>
                </div>
                <div class="testimonial">
                    <p>The team at AI Founders Hub is highly knowledgeable and professional</p>
                    <p>- Jane Smith, CTO of ABC Inc.</p>
                </div>
                <div class="testimonial">
                    <p>We have seen significant improvements in our business operations since working with AI Founders Hub</p>
                    <p>- Bob Johnson, CEO of DEF Ltd.</p>
                </div>
            </section>
            <!-- Contact Form Section -->
            <section id="contact">
                <h2>Get in Touch</h2>
                <form>
                    <input type="text" placeholder="Name" required>
                    <input type="email" placeholder="Email" required>
                    <textarea placeholder="Message" required></textarea>
                    <button>Send</button>
                </form>
            </section>
            <!-- Footer Section -->
            <footer>
                <p>&copy; 2024 AI Founders Hub</p>
            </footer>
            <script src="script.js"></script>
        </body>
        </html>
        ''')

    # Create the CSS file
    with open('style.css', 'w') as file:
        file.write('''
        /* Global Styles */
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f9f9f9;
        }
        /* Hero Section Styles */
        #hero {
            background-color: #337ab7;
            color: #fff;
            padding: 100px;
            text-align: center;
        }
        #hero h1 {
            font-size: 36px;
            margin-bottom: 20px;
        }
        #hero p {
            font-size: 18px;
            margin-bottom: 30px;
        }
        #hero button {
            background-color: #fff;
            color: #337ab7;
            border: none;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
        }
        /* Services Section Styles */
        #services {
            padding: 100px;
        }
        .service {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .service h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        /* Testimonials Section Styles */
        #testimonials {
            padding: 100px;
        }
        .testimonial {
            background-color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        /* Contact Form Section Styles */
        #contact {
            padding: 100px;
        }
        form {
            max-width: 500px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
        }
        button {
            background-color: #337ab7;
            color: #fff;
            border: none;
            padding: 10px 20px;
            font-size: 18px;
            cursor: pointer;
        }
        /* Footer Section Styles */
        footer {
            background-color: #337ab7;
            color: #fff;
            padding: 10px;
            text-align: center;
            clear: both;
        }
        ''')

    # Create the JavaScript file
    with open('script.js', 'w') as file:
        file.write('''
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
        ''')

# Create the website
create_website()

# Run the HTTP server
try:
    # Create the HTTP server
    with socketserver.TCPServer(("", 8000), RequestHandler) as httpd:
        print("Serving at port 8000")
        # Open the website in the default web browser
        webbrowser.open("http://localhost:8000")
        # Start the HTTP server
        httpd.serve_forever()
except Exception as e:
    # Handle any exceptions
    print(f"An error occurred: {e}")