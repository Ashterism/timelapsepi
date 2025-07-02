# 📸 TimelapsePi Test Plan
This outlines unit/integration tests to implement across the timelapse project.

## ✅ Existing Tests
- [x] `set_active_session()` writes active session path to file
- [x] `get_active_session()` reads active session path
- [x] Returns `None` if file missing

---

## 🔜 To Implement

### Session Management (unit)
- [ ] `clear_active_session()` clears the session file
- [ ] Returns `None` if file content is corrupted or invalid
- [ ] Prevent `set_active_session()` if session folder doesn’t exist (optional)

### Timelapse Runner (integration)
- [ ] `start` command writes session folder, config JSON, and sets active session
- [ ] `runner` logs start, takes expected number of photos, completes
- [ ] `stop` clears active session
- [ ] Validate `status` reads correct folder and config

### Test Photo
- [ ] `test` runs `take_photo()`, stores latest.jpg and latest.json
- [ ] `latest.json` contains timestamp and path

### Presets
- [ ] Loads preset from CLI and updates config/env as expected
- [ ] Invalid preset returns error but does not crash
- [ ] Correct log entry created

### Flags + Config
- [ ] `toggle` flips value in config.env and persists
- [ ] `refresh` reloads new value

### Error Handling
- [ ] Graceful handling when session/config folders missing
- [ ] Log errors for failed subprocesses