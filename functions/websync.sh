# FUNCTION: pull_git()
pull_git() {
  if [ "$GITHUB_PULL" == "true" ]; then
    if [ "$ONLINE" == "true" ]; then
      log "[INFO] Pulling latest from GitHub..."
      OUTPUT=$(timeout 20s /usr/bin/git pull origin main 2>&1)
      if [ $? -ne 0 ]; then
        log "[ERROR] git pull failed at $(date)"
      else
        log "[INFO] GitHub pull successful"
        echo "$OUTPUT" | grep -E "files? changed" | while read -r line; do
          log "[INFO] Git summary: $line"
        done
      fi
    else
      log "[INFO] GitHub sync skipped - no internet"
    fi
  else
    log "[INFO] GitHub pull disabled by config"
  fi
}

 # FUNCTION: upload_firebase()
upload_firebase() {
  if [ "$FIREBASE_UPLOAD" == "true" ]; then
    if [ "$ONLINE" == "true" ]; then
      log "[INFO] Uploading to Firebase..."
      OUTPUT=$(timeout 20s /usr/bin/python3 upload_status.py 2>&1)
      if [ $? -ne 0 ]; then
        log "[ERROR] upload_status.py failed at $(date)"
      else
        log "[INFO] Firebase upload complete"
        SUMMARY=$(echo "$OUTPUT" | grep -Eo '[0-9]+ files? uploaded')
        if [ -n "$SUMMARY" ]; then
          log "[INFO] Firebase summary: $SUMMARY"
        else
          log "[INFO] Firebase output (no summary match): $OUTPUT"
        fi
      fi
    else
      log "[INFO] Firebase upload skipped - no internet"
    fi
  else
    log "[INFO] Firebase upload disabled by config"
  fi
}