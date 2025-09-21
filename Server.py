from flask import Flask, request, jsonify
import pyrebase
import time
import os

app = Flask(__name__)

# Firebase Konfiguration aus Environment Variables
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

@app.route('/')
def home():
    return "✅ Server ist online!"

@app.route('/register_code', methods=['POST'])
def register_code():
    try:
        data = request.json
        user_id = data.get('user_id')
        code = data.get('code')
        discord_name = data.get('discord_name')
        
        db.child("pending_codes").child(user_id).set({
            "code": code,
            "discord_name": discord_name,
            "timestamp": time.time(),
            "used": False
        })
        
        return jsonify({"status": "success"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.json
        code = data.get('code')
        
        pending_codes = db.child("pending_codes").get().val() or {}
        
        for user_id, code_data in pending_codes.items():
            if code_data.get('code') == code and not code_data.get('used'):
                db.child("verified_users").child(user_id).set({
                    "user_id": user_id,
                    "code": code,
                    "timestamp": time.time(),
                    "status": "verified"
                })
                
                db.child("pending_codes").child(user_id).update({"used": True})
                
                return jsonify({
                    "status": "success", 
                    "message": "Erfolgreich verifiziert!"
                })
        
        return jsonify({"status": "error", "message": "Ungültiger Code!"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
