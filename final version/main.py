# Entry point required by the assignment.
# Run: python main.py
from website import create_app

app = create_app()

if __name__ == "__main__":
    # The tutor can run this file directly
    app.run(host="127.0.0.1", port=5000, debug=False)
