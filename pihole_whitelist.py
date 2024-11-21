from flask import Flask, request, redirect, render_template_string, flash, send_file
import subprocess
import urllib.parse
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Serve the HTML form
@app.route('/', methods=['GET'])
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pi-hole Whitelist</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                text-align: center;
            }
            .container {
                background-color: white;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border-radius: 8px;
                width: 300px;
            }
            input, button {
                padding: 10px;
                margin-top: 10px;
                width: 100%;
                box-sizing: border-box;
                border-radius: 5px;
            }
            label {
                display: block;
                margin-bottom: 5px;
            }
            button {
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
                margin-bottom: 10px;
            }
            button:hover {
                background-color: #45a049;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            .error {
                color: red;
                margin-bottom: 15px;
            }
            .disable-buttons {
                display: flex;
                flex-direction: row;
                gap: 10px;
            }
            .disable-btn {
                flex: 1;
                background-color: #03c0ef;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Holland Domain Whitelist</h1>
            {% with messages = get_flashed_messages(with_categories=true) %}
              {% if messages %}
                <div class="error">{{ messages[0][1] }}</div>
              {% endif %}
            {% endwith %}
            <form action="/whitelist" method="POST">
                <label for="url">Enter URL:</label>
                <input type="text" id="url" name="url" required>
                <button type="submit">Add to Whitelist</button>
            </form>
            
            <h2>Disable</h2>
            <div class="disable-buttons">
                <button class="disable-btn" onclick="window.location.href='/disable/5m'">5 mins</button>
                <button class="disable-btn" onclick="window.location.href='/disable/20m'">20 mins</button>
                <button class="disable-btn" onclick="window.location.href='/disable/1h'">1 hours</button>
            </div>
        </div>
    </body>
    </html>
    """)

# Function to extract domain from URL
def get_domain(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        if not domain:
            domain = parsed_url.path

        # Strip 'www.' prefix if present
        domain = domain.replace('www.', '')

        # Reject URLs with query parameters or fragments
        if parsed_url.query or parsed_url.fragment:
            return None

        # Check for a valid domain pattern
        if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", domain):
            return None

        return domain
    except Exception:
        return None

# Handle the form submission
@app.route('/whitelist', methods=['POST'])
def whitelist():
    url = request.form['url']
    domain = get_domain(url)

    if domain:
        regex_pattern = f"(\\.|^){domain}$"
        subprocess.run(["pihole", "--white-regex", regex_pattern], capture_output=True)
        return redirect('/')
    else:
        flash('Invalid URL. Please enter a valid domain without query parameters or fragments.', 'error')
        return redirect('/')

# Handle Pi-hole disable for different time intervals
@app.route('/disable/<duration>', methods=['GET'])
def disable(duration):
    valid_durations = ['5m', '20m', '1h']
    if duration in valid_durations:
        subprocess.run(["pihole", "disable", duration], capture_output=True)
        flash(f'Pi-hole disabled for {duration}.', 'success')
    else:
        flash('Invalid duration.', 'error')
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)

