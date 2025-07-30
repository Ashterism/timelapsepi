from pathlib import Path

p = Path('/home/ash/timelapse/sessions/session_20250729_094249')
print("Exists:", p.exists())
print("Is directory:", p.is_dir())