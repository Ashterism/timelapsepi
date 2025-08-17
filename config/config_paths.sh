#!/bin/bash

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ROOT_DIR

CONFIG_FILE="$ROOT_DIR/config/config.env"
PRESETS_FILE="$ROOT_DIR/config/presets.env"
LOGS_DIR="$ROOT_DIR/data/logs"
MODE_CONTROL_FILE="$ROOT_DIR/config/mode_control.env"
PRESET_LOADER="$ROOT_DIR/config/load_preset.sh"

LOGGING_SH="$ROOT_DIR/operations/logging.sh"
NETWORK_SH="$ROOT_DIR/operations/network.sh"
DATA_SYNC_SH="$ROOT_DIR/operations/data_sync.sh"
WEBSERVER_SH="$ROOT_DIR/interfaces/webserver.sh"
MODE_CONTROL_SH="$ROOT_DIR/operations/mode_control.sh"

export UVICORN_PATH=$(command -v uvicorn 2>/dev/null || echo "$HOME/.local/bin/uvicorn")
