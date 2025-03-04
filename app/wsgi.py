import os
import sys

# Add the app directory to Python path
app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app'))
sys.path.insert(0, app_dir)

from main import app

if __name__ == "__main__":
    app.run()