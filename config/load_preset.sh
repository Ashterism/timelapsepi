# === File: load_preset.sh ===
#!/bin/bash

PRESETS_FILE="/home/ash/timelapse/defaults/presets.env"
CONFIG_FILE="/home/ash/timelapse/config.env"

MODE_NAME="$1"

if [ -z "$MODE_NAME" ]; then
  echo "❌ No preset name provided"
  exit 1
fi

if ! grep -q "^\[$MODE_NAME\]" "$PRESETS_FILE"; then
  echo "❌ Preset '$MODE_NAME' not found in $PRESETS_FILE"
  exit 1
fi

# Clear the existing config file
echo "# Auto-generated config from preset: $MODE_NAME" > "$CONFIG_FILE"
echo "MODE_CONTROL=system" >> "$CONFIG_FILE"

grep -A10 "^\[$MODE_NAME\]" "$PRESETS_FILE" | \
  tail -n +2 | \
  grep -v "^\[" | \
  grep -v "^--" | \
  sed '/^$/d' >> "$CONFIG_FILE"