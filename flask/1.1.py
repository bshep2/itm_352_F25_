"""
Simple Flask Application with Debug Mode
This creates a web server with a single route that displays a welcome message.
"""

from flask import Flask

# Create Flask application instance
app = Flask(__name__)

# Define route for the home page
@app.route('/')
def home():
    """
    Handle requests to the root URL
    Returns a personalized welcome message
    """
    return "Welcome to [Your Name]'s web site!"

# Run the application
if __name__ == '__main__':
    print("=" * 60)
    print("Starting Flask Application in Debug Mode")
    print("=" * 60)
    print("\nServer will be accessible at:")
    print("  - http://127.0.0.1:5000")
    print("  - http://localhost:5000")
    print("\nPress CTRL+C to stop the server")
    print("=" * 60)
    
    # Run with debug mode enabled
    app.run(debug=True, host='127.0.0.1', port=5000)