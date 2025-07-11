#
Notes 
- add samba?
- add exiftool
- pijuice buttons need access to the home directory for buttons to work - after bookworm requires you to run chmod 750 /home/ash (where ash=home directory)
  


# timelapsepi

> Power-resilient Raspberry Pi logging and status system with PiJuice zero + Firebase
> Timelapse tool

Also see: https://github.com/PiSupply/PiJuice/blob/master/Software/README.md

---

## 📋 Overview

`timelapsepi` is a modular Raspberry Pi logging system designed for remote, solar-powered operation.

It logs power, battery, and system data using PiJuice, stores it locally, and (when connected) uploads it to Firebase Firestore for remote monitoring — e.g. via: [Ashterix | Pi Status](https://ashterix.com/status)

---

## 📦 Repo Contents

- `log_status.py` — Logs system + PiJuice data as JSON
- `upload_status.py` — Uploads log files to Firebase
- `tma1.sh` — Cron-triggered script that coordinates logging, uploads, Git sync, hotspot/wifi checks
- `timelapsepi.py` — CLI to view + toggle config flags (e.g. logging, uploads, hotspot)
- `scripts/` — Contains stub or modular scripts (e.g. Git pull, start hotspot)
- `_local/` — Stores logs locally (ignored by Git)
- `status.json` — Most recent system snapshot (for debug/quick UI display)
- `config.env` — Toggles behaviour (logging, Firebase, Git, Wi-Fi mode)
- `web/webserver.py` — FastAPI webserver to trigger captures and monitor status
- `functions/photo.sh` — Captures photo + writes metadata  
- `functions/webserver.sh` — Starts/stops Flask server for remote control

---

## 🔧 Requirements

Assumes working directory is `/home/pi/timelapse/`.

If using a different path, update:

- Paths in `tma1.sh`, `log_status.py`, `upload_status.py`
- Cronjob (see below)

---

### 1. Install PiJuice software

> sudo apt-get update
> sudo apt-get install pijuice-base

---

### 2. Enable I2C for PiJuice

> sudo raspi-config

# Interface Options > I2C > Enable

---

### 3. Install Python dependencies

> sudo pip3 install firebase-admin python-dotenv

---

### 4. Create `_local/logs` directory

```bash
mkdir -p /home/pi/timelapse/_local/logs
```

---

### 5. Set up Firebase

- Go to https://console.firebase.google.com and create a project
- Enable Firestore (start in test mode)
- Go to: Project Settings > Service Accounts > Generate Private Key
- Save the `.json` key to:

```
/home/pi/firebase-creds.json
```

> 🔒 **Never commit this file to Git!**

Edit `upload_status.py` if using a different path:

> cred = credentials.Certificate("/home/pi/firebase-creds.json")

---

### 6. Install Camera + Metadata Tools

```bash
sudo apt update
sudo apt install libcamera-apps exiftool
```

- `libcamera-jpeg` is used to capture photos from the Pi Camera Module
- `exiftool` generates metadata for each image as a `.json` file

---

## 🔁 Cron Setup

Edit crontab to run the main script every 15 minutes:

> crontab -e

Add:

> */15 * * * * cd /home/ash/timelapse && /bin/bash tma1.sh 2>&1 | ts '[%Y-%m-%d %H:%M:%S]' >> /home/ash/timelapse/data/logs/cron.log

This runs the script using bash, ensures the working directory is correct, and adds per-line timestamps using `ts` from `moreutils`.

To install `ts`, run:
sudo apt install moreutils

Make sure it's executable:

> chmod +x /home/pi/timelapse/tma1.sh

---

## 🔧 Config via `config.env`

Use this file to enable/disable modules:

> LOGGING_ENABLED=True
> FIREBASE_UPLOAD=True
> GITHUB_PULL=False
> WIFI_CLIENT_MODE=True
> WIFI_HOTSPOT=False

Change values using:

python3 timelapsepi.py

You’ll get a visual toggle menu in terminal.

---

## 🔄 Script Logic (`tma1.sh`)

Every 15 mins:

1. Logs battery/system status (if enabled)
2. Wakes + checks Wi-Fi (client mode)
3. Pulls latest code from GitHub (if enabled)
4. Uploads data to Firebase (if enabled)
5. Starts hotspot (if enabled)
6. Logs result and errors to `_local/run.log`

Offline logging is fully supported — files will sync when reconnected.

---

## 📶 Hotspot / Off-Grid Mode

See [README-hotspot-mode.md](README-hotspot-mode.md) for full instructions to set up:

- A direct-connect hotspot
- Static IP and DHCP server
- Toggle button to switch between Wi-Fi client and hotspot

---

## ⚠️ Git Ignore

The `_local/` folder is ignored using `.gitignore` to prevent flooding the repo with data files:

> _local/

---

## 🧩 Git Merge Conflicts (Autoupdate)

To avoid auto-pull failures due to merge prompts, run:

> git config pull.rebase false
> git config --global core.editor true

---

## 📡 Full Hotspot Setup Guide (Off-Grid Mode)

## 🌐 Enabling Direct Wi-Fi Hotspot Mode (for Off-Grid Use)

This allows your Pi to act as a Wi-Fi access point, so you can connect directly to it (without a router) in the field.

### ✅ One-Time Setup Steps

Run all commands from your Pi while connected to a regular Wi-Fi network (client mode):

---

### 1. Install required packages

> sudo apt update
> sudo apt install hostapd dnsmasq
> sudo systemctl unmask hostapd
> sudo systemctl disable hostapd

---

### 2. Create `/etc/hostapd/hostapd.conf`

> sudo nano /etc/hostapd/hostapd.conf

Paste the following:

> interface=wlan0
> driver=nl80211
> ssid=timelapsepi
> hw_mode=g
> channel=7
> wmm_enabled=0
> auth_algs=1
> ignore_broadcast_ssid=0

This creates an **open network** called `timelapsepi`. You can add WPA settings later if needed.

---

### 3. Configure a static IP on `wlan0`

> sudo nano /etc/dhcpcd.conf

Add this at the bottom:

> interface wlan0
>     static ip_address=192.168.4.1/24
>     nohook wpa_supplicant

---

### 4. Set up DHCP server

> sudo nano /etc/dnsmasq.conf

Add:

> interface=wlan0
> dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h

---

### 5. (Optional) Toggle hotspot mode via PiJuice button

If you’ve set up a `toggle_wifi_mode.sh` script and mapped it via:

> pijuice_cli buttons set custom long /home/ash/toggle_wifi_mode.sh

Then a long press will switch between client and hotspot modes.

---

### 6. Enable in config

Make sure `config.env` contains:

> WIFI_MODE=hotspot

Your cron-driven `tma1.sh` will now re-check and reassert the hotspot mode every 15 minutes.

---

🧪 Once tested, you can safely start hotspot mode in the desert and connect from your laptop to the Pi without needing any router or mobile data.

---

## 📷 Web Interface for Capturing Photos

If WEBSERVER_ENABLED=true is set in config.env, a FastAPI-based web interface will run on port 5000.

Access from a browser:
- `http://<pi-ip>:5000/` — Main interface
- `/photo` — Captures a photo + metadata
- `/latest.jpg` — Latest image preview
- `/status` — Shows uptime and network mode
- `/latest-timestamp` — Returns the timestamp of the latest photo
- `/webserverlog` — Displays recent log entries
- `/sessions` — Lists timelapse session folders

Captured photos and metadata are stored in `_local/photos/`.

To expose this interface securely over the internet, consider using NGINX as a reverse proxy with optional HTTPS via Certbot.
