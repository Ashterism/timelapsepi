import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# Load Firebase credentials
cred = credentials.Certificate("/home/ash/firebase-creds.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load local status.json
with open("/home/ash/timelapse/status.json") as f:
    status_data = json.load(f)

# Add upload timestamp
status_data["uploaded"] = datetime.utcnow().isoformat()

# Push to Firestore
doc_ref = db.collection("status_logs").document()
doc_ref.set(status_data)

print("✅ Status uploaded to Firebase.")
