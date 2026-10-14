"""Local dev entry point.

    python -m venv .venv
    .venv\Scripts\activate        (Windows)   |   source .venv/bin/activate (Unix)
    pip install -r requirements.txt
    python run.py
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
