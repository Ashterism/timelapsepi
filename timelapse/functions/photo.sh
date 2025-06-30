#!/bin/bash

# TODO: Consider adding HDR support with:
# libcamera-still --hdr 1 ...
# Requires tuning + validation

# photo.sh — photo capture and metadata tools
source "$(dirname "$BASH_SOURCE")/../../config/config_paths.sh"
source "$LOGGING_SH"

# FUNCTION: take_photo()
take_photo() {
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  local LATEST_DIR="$ROOT_DIR/data/temp/latestjpg"
  local IMAGE_PATH="$LATEST_DIR/latest.jpg"
  local RAW_META_PATH="$LATEST_DIR/raw_metadata.json"

  mkdir -p "$LATEST_DIR"

  # Photo capture (for Pi Camera type only)
  libcamera-jpeg -o "$IMAGE_PATH" --metadata "$RAW_META_PATH" --metadata-format json

  log "[INFO] Test photo captured: $IMAGE_PATH"

  write_metadata "$IMAGE_PATH" "$TIMESTAMP"
}

# FUNCTION: write_metadata()
write_metadata() {
  local IMAGE_PATH="$1"
  local TIMESTAMP="$2"
  local METADATA_PATH="${IMAGE_PATH%.jpg}.json"
  local FILENAME="$(basename "$IMAGE_PATH")"


  # sub-function: extract_exif_value
  extract_exif_value() {
    local TAG="$1"
    local FILE="$2"
    if command -v exiftool > /dev/null; then
      local VAL
      VAL=$(exiftool -s3 -"${TAG}" "$FILE" 2>/dev/null)
      if [ -z "$VAL" ]; then
        echo "unknown"
      else
        echo "$VAL"
      fi
    else
      echo "unknown"
    fi
  }

  local ISO=$(extract_exif_value ISO "$IMAGE_PATH")
  local SHUTTER=$(extract_exif_value ExposureTime "$IMAGE_PATH")
  local FOCAL_LENGTH=$(extract_exif_value FocalLength "$IMAGE_PATH")
  local CAMERA_MODEL=$(extract_exif_value Model "$IMAGE_PATH")
  local APERTURE=$(extract_exif_value Aperture "$IMAGE_PATH")
  local EXPOSURE_BIAS=$(extract_exif_value ExposureCompensation "$IMAGE_PATH")
  local METERING_MODE=$(extract_exif_value MeteringMode "$IMAGE_PATH")
  local FLASH=$(extract_exif_value Flash "$IMAGE_PATH")
  local WHITE_BALANCE=$(extract_exif_value WhiteBalance "$IMAGE_PATH")
  local IMAGE_WIDTH=$(extract_exif_value ImageWidth "$IMAGE_PATH")
  local IMAGE_HEIGHT=$(extract_exif_value ImageHeight "$IMAGE_PATH")
  local FILE_SIZE=$(extract_exif_value FileSize "$IMAGE_PATH")

  local RAW_META_PATH="${IMAGE_PATH%.*}/raw_metadata.json"

  # Extract select libcamera metadata if available
  if [ -f "$RAW_META_PATH" ]; then
    RAW_EXPOSURE_US=$(jq '.ExposureTime' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
    RAW_ANALOGUE_GAIN=$(jq '.AnalogueGain' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
    RAW_DIGITAL_GAIN=$(jq '.DigitalGain' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
    RAW_LUX=$(jq '.Lux' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
    RAW_COLOUR_TEMP=$(jq '.ColourTemperature' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
    RAW_SENSOR_TEMP=$(jq '.SensorTemperature' "$RAW_META_PATH" 2>/dev/null || echo "unknown")
  fi

  cat <<EOF > "$METADATA_PATH"
{
  "filename": "$FILENAME",
  "timestamp": "$(date -Is)",
  "latest": true,
  "camera": "$CAMERA_MODEL",
  "settings": {
    "iso": "$ISO",
    "shutter_speed": "$SHUTTER",
    "aperture": "$APERTURE",
    "exposure_bias": "$EXPOSURE_BIAS",
    "focal_length": "$FOCAL_LENGTH",
    "metering_mode": "$METERING_MODE",
    "flash": "$FLASH",
    "white_balance": "$WHITE_BALANCE",
    "image_width": "$IMAGE_WIDTH",
    "image_height": "$IMAGE_HEIGHT",
    "file_size": "$FILE_SIZE"
  },
  "raw_metadata": {
    "exposure_us": "$RAW_EXPOSURE_US",
    "analogue_gain": "$RAW_ANALOGUE_GAIN",
    "digital_gain": "$RAW_DIGITAL_GAIN",
    "lux": "$RAW_LUX",
    "colour_temp": "$RAW_COLOUR_TEMP",
    "sensor_temp_c": "$RAW_SENSOR_TEMP"
  }
}
EOF

  log "[INFO] Metadata saved: ${METADATA_PATH}"
}

# If the script is run directly (not sourced), call take_photo
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  take_photo
fi