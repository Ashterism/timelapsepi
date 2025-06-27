#!/bin/bash
source /home/ash/timelapse/config/config_paths.sh

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

awk -v section="[$MODE_NAME]" '
  $0 == section { found=1; next }
  /^\[.*\]/ { if(found) exit }
  found && NF { print }
' "$PRESETS_FILE" >> "$CONFIG_FILE"

echo "$(date): Loaded preset '$MODE_NAME'" >> "$LOGS_DIR/preset.log"