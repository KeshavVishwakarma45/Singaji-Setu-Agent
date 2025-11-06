from app import app, socketio
import os

# This is what Gunicorn will import
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)