#!/bin/bash

# Create new folder structure
mkdir -p operations/pijuice
mkdir -p interfaces/cli
mkdir -p interfaces/web
mkdir -p timelapse/functions
mkdir -p timelapse/runner
mkdir -p data/sessions
mkdir -p data/logs
mkdir -p data/temp

# Backup original files
mkdir -p _legacy_backup
cp -r functions _legacy_backup/
cp config.env _legacy_backup/
cp *.sh _legacy_backup/
cp *.py _legacy_backup/
cp web _legacy_backup/

# Move shell scripts to operations
mv functions/logging.sh operations/
mv functions/network.sh operations/
mv functions/websync.sh operations/data_sync.sh

# Move status scripts to operations
mv log_status.py operations/
mv upload_status.py operations/

# Move photo functions to timelapse
mv functions/photo.sh timelapse/functions/

# Move run_all and config
mv run_all.sh ./
mv config.env ./
mv README.md ./

# Move web interface to interfaces
mv web/index.html interfaces/web/
mv web/photo.js interfaces/web/
mv web/style.css interfaces/web/
mv webserver.py interfaces/web/
mv functions/webserver.sh interfaces/

# Move interface controls
mv toggle_wifi_mode.py interfaces/
mv timelapsepi.py interfaces/cli/

# Done message
echo "✅ Refactor complete. Original files backed up to _legacy_backup/"