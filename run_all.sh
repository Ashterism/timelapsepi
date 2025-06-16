#!/bin/bash

cd /home/ash/timelapse

# Update from GitHub
/usr/bin/git pull origin main

# Log battery + power status
/usr/bin/python3 log_status.py

# Upload to Firebase
/usr/bin/python3 upload_status.py
