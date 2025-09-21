from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db
import time
import os

# Firebase Initialization
try:
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "token_uri": "https://oauth2.googleapis.com/token",
    })
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })
except:
    print("Firebase Initialization failed")

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Server ist online!"

@app.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.json
        code = data.get('code')
        
        # Einfache Test-Logik
        return jsonify({
            "status": "success", 
            "message": "Erfolgreich verifiziert!"
        })
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
