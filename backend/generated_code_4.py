# Import the necessary libraries
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RequestHandler(BaseHTTPRequestHandler):
    # Define the HTTP request handler
    def do_GET(self):
        # Handle GET requests
        try:
            # Send a response back to the client
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Hello, World!")
        except Exception as e:
            # Log any exceptions that occur
            logging.error(f"Error handling GET request: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Internal Server Error")

def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    # Define the server class and handler class
    try:
        # Create the server
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        # Log a message indicating the server is running
        logging.info(f"Starting HTTP server on port {port}...")
        # Start the server
        httpd.serve_forever()
    except KeyboardInterrupt:
        # Handle the case where the server is stopped with Ctrl+C
        logging.info("Stopping HTTP server...")
    except Exception as e:
        # Log any exceptions that occur
        logging.error(f"Error starting HTTP server: {str(e)}")

if __name__ == "__main__":
    # Run the server
    run_server()