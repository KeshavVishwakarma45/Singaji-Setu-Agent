import os
os.environ.setdefault('FLASK_ENV', 'production')

from app import app

# This is what Gunicorn will import
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)