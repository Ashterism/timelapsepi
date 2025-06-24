import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


# Set log directory
log_dir = "/home/ash/timelapse/logs"
os.makedirs(log_dir, exist_ok=True)

# Load Firebase credentials
cred = credentials.Certificate("/home/ash/firebase-creds.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Upload all log files
for filename in os.listdir(log_dir):
    if not filename.endswith(".json"):
        continue

    filepath = os.path.join(log_dir, filename)
    
    try:
        with open(filepath, "r") as f:
            data = json.load(f)

        data["uploaded"] = datetime.utcnow().isoformat()
        db.collection("status_logs").add(data)

        os.remove(filepath)
        print(f"✅ Uploaded and removed {filename}")

    except Exception as e:
        print(f"❌ Failed to upload {filename}: {e}")