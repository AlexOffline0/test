from flask import Flask

# Create an instance of the Flask class
app = Flask(__name__)

# Use the route() decorator to bind a URL to a function
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Optional: Add the following to run the app directly
if __name__ == '__main__':
    app.run(debug=True)
