 # Function: pull_git()
pull_git() {
  if [ "$GITHUB_PULL" == "True" ]; then
    if [ "$ONLINE" == "true" ]; then
      log "[INFO] Pulling latest from GitHub..."
      if ! timeout 20s /usr/bin/git pull origin main; then
        log "[ERROR] git pull failed at $(date)"
      fi
    else
      log "[INFO] GitHub sync skipped - no internet"
    fi
  else
    log "[INFO] GitHub pull disabled by config"
  fi
}

 # Function: upload_firebase()
upload_firebase() {
  if [ "$FIREBASE_UPLOAD" == "True" ]; then
    if [ "$ONLINE" == "true" ]; then
      log "[INFO] Uploading to Firebase..."
      if ! timeout 20s /usr/bin/python3 upload_status.py; then
        log "[ERROR] upload_status.py failed at $(date)"
      fi
    else
      log "[INFO] Firebase upload skipped - no internet"
    fi
  else
    log "[INFO] Firebase upload disabled by config"
  fi
}