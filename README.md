# timelapsepi

# TimelapsePi Status Logger

This project logs power, battery, and system data from a Raspberry Pi using PiJuice, and uploads it to Firebase for display on a remote status dashboard (e.g. [Ashterix | Pi Status](https://ashterix.com/status)).

## 📦 What This Repo Includes

- `log_status.py` — Logs system and PiJuice status data every 15 minutes
- `upload_status.py` — Uploads those logs to Firebase Firestore
- `run_all.sh` — Cron-triggered script to run both the above
- `_local/` (ignored by Git) — Where logs are stored before upload
- `status.json` — Most recent log (for quick debugging or display)

## 🔧 Requirements (Not Included in Repo)

This setup assumes your working directory is /home/pi/timelapse/

If you place the repo elsewhere, update paths in:
- run_all.sh
- log_status.py
- upload_status.py
- Your cronjob (crontab -e)

These must be set up manually on each Pi before it works:

### 1. Install PiJuice software
> sudo apt-get update

> sudo apt-get install pijuice-base

### 2. Install Python dependencies
> sudo pip3 install firebase-admin

### 3. Enable PiJuice I2C access
> sudo raspi-config  

Interface Options > I2C > Enable

### 4. Create _local directory
This is where logs are stored and queued before upload:

> mkdir -p /home/pi/timelapse/_local/logs

### 5. Set up Firebase
You need a Firebase project and Firestore enabled.

Go to https://console.firebase.google.com and create a project

In the Firebase Console, go to: Build > Firestore Database and click Create Database (start in test mode)

Go to: Project Settings > Service Accounts

Click 'Generate New Private Key' and save the .json file

Place it on your Pi at:

> /home/pi/firebase-creds.json

**🔒 Do not commit this file to the repo!**

Update the path in upload_status.py if you place the key elsewhere:

> cred = credentials.Certificate("/home/pi/firebase-creds.json")

## 🔁 Cron Setup
Add the following to your crontab to run every 15 minutes:

> crontab -e

> */15 * * * * /home/pi/timelapse/run_all.sh

Make sure the script is executable:

> chmod +x /home/pi/timelapse/run_all.sh

## 🔄 What It Does
Every 15 minutes:

1. log_status.py logs data from the PiJuice and system to a timestamped .json in _local/logs/
2. upload_status.py attempts to upload all .json files in that folder to Firebase
3. Files are deleted after successful upload; failures remain and are retried next time

This ensures offline resilience — no data is lost if Wi-Fi drops.

## ⚠️ Git Ignore
The _local/ folder is ignored using .gitignore to prevent flooding the repo with data files:

> _local/

## Set default behaviour for git merge
To avoid conflicts preventing the autoupdate function working run this on the pi:

> git config pull.rebase false

> git config --global core.editor true
