#!/bin/bash

run_mode_control() {
  source "$HOME/timelapse/config/config_paths.sh"
  source "$LOGGING_SH"

  # Load mode control
  if ! source "$MODE_CONTROL_FILE"; then
    echo "[ERROR] mode_control.env not found or failed to load!"
    exit 1
  fi

  log "[INFO] Mode control set to: $MODE_CONTROL"
  log "[INFO] Active preset: $ACTIVE_PRESET"

  # Apply preset if system mode
  if [ "$MODE_CONTROL" == "system" ]; then
    log "[INFO] SYSTEM mode enabled — reloading preset: $ACTIVE_PRESET"

    if [[ -z "$PRESET_LOADER" || ! -f "$PRESET_LOADER" ]]; then
      log "[ERROR] Invalid or missing preset loader at: $PRESET_LOADER"
      exit 1
    fi

    bash "$PRESET_LOADER" "$ACTIVE_PRESET"
  else
    log "[INFO] USER mode — preserving existing config.env"
  fi
}

export -f run_mode_control
