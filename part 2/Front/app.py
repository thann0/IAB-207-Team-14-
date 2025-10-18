# Front/app.py
"""
Entry point to run the app with `python Front/app.py`.
It imports the Backend package (one level up) and uses create_app().
"""
import os
import sys

# Ensure Python can import the Backend package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Backend import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    # You can set host/port if needed
    app.run(debug=True)
