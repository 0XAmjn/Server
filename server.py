from flask import Flask, request, jsonify
import pyrebase
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Firebase Konfiguration
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID")
}

# Pyrebase Initialisierung
firebase = pyrebase.initialize_app(firebase_config)
database = firebase.database()

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
        timestamp = time.time()
        
        # Code in Firebase speichern
        database.child("pending_codes").child(user_id).set({
            "code": code,
            "discord_name": discord_name,
            "timestamp": timestamp,
            "used": False,
            "status": "pending"
        })
        
        print(f"✅ Code registriert: {code} für {discord_name}")
        return jsonify({"status": "success", "message": "Code registriert"})
        
    except Exception as e:
        print(f"❌ Fehler in register_code: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/verify_code', methods=['POST'])
def verify_code():
    try:
        data = request.json
        code = data.get('code')
        
        # Alle pending codes aus Firebase holen
        pending_codes = database.child("pending_codes").get().val() or {}
        
        for user_id, code_data in pending_codes.items():
            if (code_data.get('code') == code and 
                not code_data.get('used') and 
                time.time() - code_data.get('timestamp', 0) < 600):  # 10 Minuten gültig
                
                # Verifizierung erfolgreich
                database.child("verified_users").child(user_id).set({
                    "user_id": user_id,
                    "code": code,
                    "timestamp": time.time(),
                    "status": "verified"
                })
                
                # Als verwendet markieren
                database.child("pending_codes").child(user_id).update({"used": True})
                
                print(f"✅ Verifizierung erfolgreich für Code: {code}")
                return jsonify({
                    "status": "success", 
                    "message": "Erfolgreich verifiziert!"
                })
        
        print(f"❌ Ungültiger Code: {code}")
        return jsonify({"status": "error", "message": "Ungültiger oder abgelaufener Code!"})
        
    except Exception as e:
        print(f"❌ Fehler in verify_code: {e}")
        return jsonify({"status": "error", "message": "Server error"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": time.time(),
        "server_url": "https://airy-compassion.railway.app"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server starting on port {port}")
    print(f"🌐 Firebase Project: {firebase_config['projectId']}")
    app.run(host='0.0.0.0', port=port, debug=False)
