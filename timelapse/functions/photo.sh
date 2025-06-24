#!/bin/bash
# photo.sh — photo capture and metadata tools
source ../../operations/logging.sh

# FUNCTION: take_photo()
take_photo() {
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  IMAGE_DIR="/home/ash/timelapse/_local/photos"
  LATEST_PATH="/home/ash/timelapse/_local/latest.jpg"
  IMAGE_PATH="$IMAGE_DIR/$TIMESTAMP.jpg"

  mkdir -p "$IMAGE_DIR"

  # Photo capture (for Pi Camera type only)
  libcamera-jpeg -o "$IMAGE_PATH"

  # Update 'latest' image
  cp "$IMAGE_PATH" "$LATEST_PATH"

  log "[INFO] Photo captured: $IMAGE_PATH"

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
  }
}
EOF

  log "[INFO] Metadata saved: ${METADATA_PATH}"
}

# If the script is run directly (not sourced), call take_photo
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  take_photo
fi