from flask import Flask, request, render_template_string, send_from_directory
import os
import glob
from scraper.scraper import Backend
from scraper.communicator import Communicator

# Folder where the scraper saves the output file
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

app = Flask(__name__)

# A simple frontend object for our Communicator so that messages can be captured
class FlaskFrontend:
    def __init__(self):
        self.messages = []
        self.outputFormatValue = ""  # This needs to be set
    def messageshowing(self, message):
        self.messages.append(message)
    def end_processing(self):
        pass

INDEX_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Google Maps Scraper - Web Frontend</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #34495e;
            font-weight: 500;
        }
        input[type="text"], select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        .checkbox-group {
            margin: 15px 0;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            width: 100%;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        .error {
            color: #e74c3c;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #e74c3c;
            background-color: #fdf7f7;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Google Maps Scraper</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="post">
            <div class="form-group">
                <label for="searchquery">Search Query:</label>
                <input type="text" id="searchquery" name="searchquery" placeholder="Enter location or business type...">
            </div>
            
            <div class="form-group">
                <label for="outputformat">Output Format:</label>
                <select id="outputformat" name="outputformat">
                    <option value="excel">Excel (.xlsx)</option>
                    <option value="csv">CSV</option>
                    <option value="json">JSON</option>
                </select>
            </div>
            
            <div class="checkbox-group">
                <label>
                    <input type="checkbox" id="headless" name="headless">
                    Run in Headless Mode (faster, runs in background)
                </label>
            </div>
            
            <button type="submit">Start Scraping</button>
        </form>
    </div>
</body>
</html>
"""

RESULT_TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Scraping Result</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .success {
            text-align: center;
            margin: 20px 0;
        }
        .download-btn {
            display: inline-block;
            background-color: #27ae60;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
            transition: background-color 0.3s;
        }
        .download-btn:hover {
            background-color: #219a52;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #3498db;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Scraping Results</h1>
        
        {% if file_url %}
            <div class="success">
                <p>✅ Scraping completed successfully!</p>
                <a href="{{ file_url }}" class="download-btn">⬇️ Download Results</a>
            </div>
        {% endif %}
        
        <a href="/" class="back-link">← Back to Search</a>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            searchquery = request.form.get("searchquery", "").strip().lower()
            outputformat = request.form.get("outputformat", "").strip().lower()
            headless = 1 if request.form.get("headless") == "on" else 0

            if not searchquery or not outputformat:
                error = "Missing search query or output format."
                return render_template_string(INDEX_TEMPLATE, error=error)
            
            flask_front = FlaskFrontend()
            flask_front.outputFormatValue = outputformat
            Communicator.set_frontend_object(flask_front)

            backend = Backend(searchquery, outputformat, headless)
            backend.mainscraping()

            pattern = os.path.join(OUTPUT_FOLDER, f"{searchquery} - pingme output*")
            files = glob.glob(pattern)
            if files:
                latest_file = max(files, key=os.path.getmtime)
                filename = os.path.basename(latest_file)
                file_url = f"/download/{filename}"
            else:
                file_url = None
            
            return render_template_string(RESULT_TEMPLATE, 
                                       messages=flask_front.messages, 
                                       file_url=file_url)
                                       
        except Exception as e:
            error = f"An error occurred during scraping: {str(e)}"
            return render_template_string(INDEX_TEMPLATE, error=error)
            
    return render_template_string(INDEX_TEMPLATE, error=None)

@app.route("/download/<path:filename>")
def download_file(filename):
    try:
        # Ensure the requested file exists and is within OUTPUT_FOLDER
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(file_path):
            return "File not found", 404
        
        # Sanitize filename to prevent directory traversal
        filename = os.path.basename(filename)
        
        # Return the file as an attachment
        return send_from_directory(
            OUTPUT_FOLDER, 
            filename,
            as_attachment=True,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)