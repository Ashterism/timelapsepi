// This script handles taking a new photo and updating the preview image

let lastTimestamp = null;

// Called when the "Take Test Photo" button is clicked
// New version: disables the button, sends POST to /photo, then checks for new timestamp and updates the image.
async function takePhoto() {
  const btn = document.querySelector('button[onclick="takePhoto()"]');
  btn.disabled = true;
  btn.textContent = "📸 Taking...";

  try {
    console.log("⏳ Sending photo request...");
    const photoRes = await fetch('/photo', { method: 'POST' });
    console.log("📸 Photo fetch status:", photoRes.status);
    if (!photoRes.ok) throw new Error('Photo failed');

    console.log("✅ Photo complete, fetching timestamp...");
    const res = await fetch('/latest-timestamp');
    const newTimestamp = await res.text();

    if (newTimestamp !== lastTimestamp) {
      console.log("🆕 New photo detected.");
      const img = document.getElementById("preview-img");
      img.src = `/latest.jpg?cachebust=${new Date().getTime()}`;
      // Fetch and show metadata
      const metaRes = await fetch('/latest.json');
      const meta = await metaRes.json();
      const raw = meta.timestamp;
      let formatted = "unknown";
      if (raw) {
        const date = new Date(raw);
        formatted = date.toLocaleString(undefined, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      }
      document.getElementById("meta-timestamp").textContent = formatted;
      document.getElementById("meta-iso").textContent = meta.settings.iso || "unknown";
      document.getElementById("meta-shutter").textContent = meta.settings.shutter_speed || "unknown";
      document.getElementById("meta-aperture").textContent = meta.settings.aperture || "unknown";
      document.getElementById("meta-filesize").textContent = meta.settings.file_size || "unknown";
      document.getElementById("meta-resolution").textContent = `${meta.settings.image_width}×${meta.settings.image_height}` || "unknown";
      lastTimestamp = newTimestamp;
    } else {
      console.warn("⚠️ No new timestamp detected.");
    }

    resetButton(btn);
  } catch (err) {
    console.error(err);
    alert('❌ Error taking photo.');
    resetButton(btn);
  }
}

// Resets the button state after photo has been updated or if an error occurs
function resetButton(btn) {
  btn.disabled = false;
  btn.textContent = "Take Test Photo";
}

// Accordion logic: only one open at a time
document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".accordion-button");
  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const clickedAccordion = button.closest(".accordion");
      document.querySelectorAll(".accordion").forEach(acc => {
        if (acc !== clickedAccordion) acc.classList.remove("open");
      });
      clickedAccordion.classList.toggle("open");
    });
  });
});

// Menu toggle logic
document.addEventListener("DOMContentLoaded", function () {
  const menuIcon = document.querySelector(".menu-icon");
  const sideMenu = document.getElementById("sideMenu");
  menuIcon.addEventListener("click", () => {
    sideMenu.classList.toggle("open");
  });
  document.addEventListener("click", function (event) {
    const isClickInside = sideMenu.contains(event.target) || menuIcon.contains(event.target);
    if (!isClickInside) {
      sideMenu.classList.remove("open");
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      const battery = data.battery || {};
      const connection = data.connection || {};

      const batteryLevel = battery.level;
      const charging = battery.charging ? "⚡" : "";
      document.getElementById("battery-status").textContent =
        batteryLevel !== null ? `${charging}${batteryLevel}%` : "Unavailable";

      document.getElementById("connection-status").textContent =
        connection.mode === "hotspot" ? "Hotspot" : "Wi-Fi";

      document.getElementById("ip-address").textContent =
        connection.ip || "Unavailable";
    })
    .catch(err => {
      document.getElementById("battery-status").textContent = "Unavailable";
      document.getElementById("connection-status").textContent = "Unavailable";
      document.getElementById("ip-address").textContent = "Unavailable";
      console.error("Failed to fetch status:", err);
    });
});

// Fetch /latest.json on page load
document.addEventListener("DOMContentLoaded", function () {
  // Fetch latest.json to show photo metadata on initial load
  fetch('/latest.json')
    .then(res => res.json())
    .then(meta => {
      const raw = meta.timestamp;
      let formatted = "unknown";
      if (raw) {
        // Remove microseconds if present
        const cleaned = raw.split('.')[0]; // just "2025-07-26T14:43:06"
        const date = new Date(cleaned);
        if (!isNaN(date)) {
          formatted = date.toLocaleString(undefined, {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
          });
        }
      }
      document.getElementById("meta-timestamp").textContent = formatted;
      document.getElementById("meta-iso").textContent = meta.settings.iso || "unknown";
      document.getElementById("meta-shutter").textContent = meta.settings.shutter_speed || "unknown";
      document.getElementById("meta-aperture").textContent = meta.settings.aperture || "unknown";
      document.getElementById("meta-filesize").textContent = meta.settings.file_size || "unknown";
      document.getElementById("meta-resolution").textContent = `${meta.settings.image_width}×${meta.settings.image_height}` || "unknown";
    })
    .catch(err => {
      console.warn("Metadata not available:", err);
    });
});


// TIMELAPSE ///

async function startTimelapse() {
  const interval = document.getElementById('interval').value;
  const startTime = document.getElementById('start-time').value;
  const endType = document.querySelector('input[name="end-type"]:checked').value;
  // Use correct id for count input
  const count = document.getElementById('photo-count').value;
  const endTime = document.getElementById('end-time-input').value;
  // Folder input may be 'folder' or 'folder-name'
  const folderInput = document.getElementById('folder') || document.getElementById('folder-name');
  const folder = folderInput ? folderInput.value : null;

  // Validation logic before sending request
  if (!interval) {
    alert("❌ Interval is required.");
    return;
  }
  if (endType === "photo_count" && (!count || isNaN(count))) {
    alert("❌ Valid photo count is required.");
    return;
  }
  if (endType === "end_time") {
    const isoDatetimeRegex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/;
    if (!endTime || !isoDatetimeRegex.test(endTime)) {
      alert("❌ End time must be in format YYYY-MM-DDTHH:MM (e.g. 2025-04-25T15:00)");
      return;
    }
  }

  const config = {
    interval,
    start_time: startTime || null,
    end_type: endType,
    count: endType === "photo_count" ? parseInt(count) : null,
    end_time: endType === "end_time" ? endTime : null,
    folder: folder || null,
  };

  // Disable start button
  document.querySelector('button[onclick="startTimelapse()"]').disabled = true;

  try {
    const res = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const text = await res.text();
    alert(text);
    fetchSessionInfo();
    // Re-enable start button
    document.querySelector('button[onclick="startTimelapse()"]').disabled = false;
  } catch (err) {
    console.error("Error starting timelapse:", err);
    alert("❌ Failed to start timelapse.");
    // Re-enable start button
    document.querySelector('button[onclick="startTimelapse()"]').disabled = false;
  }
}

async function stopTimelapse() {
  const res = await fetch('/stop', { method: 'POST' });
  const text = await res.text();
  alert(text);
  fetchSessionInfo();
  // Reset start button state immediately
  const startBtn = document.querySelector('button[onclick="startTimelapse()"]');
  if (startBtn) {
    startBtn.disabled = false;
    startBtn.textContent = "🚀 Start Timelapse";
  }
}

async function fetchSessionInfo() {
  try {
    const res = await fetch('/sessions');
    const sessions = await res.json();

    const activeRes = await fetch('/status');
    const activeText = await activeRes.text();
    const match = activeText.match(/Session: (.*?)<br>/);
    const active = match ? match[1] : "None";
    document.getElementById("active-session").textContent = active;

    const list = document.getElementById("session-list");
    list.innerHTML = '';
    sessions.forEach(sess => {
      const li = document.createElement("li");
      li.textContent = sess;
      list.appendChild(li);
    });

    // Update start button state
    const startBtn = document.querySelector('button[onclick="startTimelapse()"]');
    if (startBtn) {
      if (active !== "None") {
        startBtn.disabled = true;
        startBtn.textContent = "Session in Progress";
      } else {
        startBtn.disabled = false;
        startBtn.textContent = "🚀 Start Timelapse";
      }
    }
  } catch (err) {
    console.error("Error loading session info:", err);
  }
}

// Timelapse toggles
document.querySelectorAll('input[name="end-type"]').forEach(el => {
  el.addEventListener('change', () => {
    const isCount = document.getElementById('end-count').checked;
    document.getElementById('end-count-group').style.display = isCount ? 'block' : 'none';
    document.getElementById('end-time-group').style.display = isCount ? 'none' : 'block';
  });
});

// Timelapse form validation & dynamic button enable/disable
function validateTimelapseInputs() {
  const interval = document.getElementById('interval').value;
  const endType = document.querySelector('input[name="end-type"]:checked').value;
  // Use correct id for count input
  const count = document.getElementById('end-count-input') ? document.getElementById('end-count-input').value : document.getElementById('photo-count').value;
  const endTime = document.getElementById('end-time-input').value;

  const valid = interval && (
    (endType === "photo_count" && count) ||
    (endType === "end_time" && endTime)
  );

  document.querySelector('button[onclick="startTimelapse()"]').disabled = !valid;
}

document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('#interval, #end-count-input, #end-time-input, input[name="end-type"], #photo-count').forEach(el => {
    el.addEventListener('input', validateTimelapseInputs);
    el.addEventListener('change', validateTimelapseInputs);
  });

  validateTimelapseInputs();
});

// SESSIONS DROPDOWN //
document.addEventListener("DOMContentLoaded", function () {
  fetch('/sessions')
    .then(res => res.json())
    .then(sessions => {
      const dropdown = document.getElementById('sessionDropdown');
      sessions.forEach(session => {
        const option = document.createElement('option');
        option.value = session.path;
        option.textContent = session.path.split('/').pop(); // show folder name only
        dropdown.appendChild(option);
      });
    });
});

// Fetches data about selected session
document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.getElementById('sessionDropdown');
  dropdown.addEventListener('change', async function () {
    const basePath = '/home/ash/timelapse/sessions';
    const sessionPath = `${basePath}/${this.value}`;
    if (!this.value) {
      const sessionDetails = document.getElementById('sessionDetails');
      if (sessionDetails) sessionDetails.style.display = 'none';
      return;
    }

    // Declare encodedPath at the top so it's available for all uses
    const encodedPath = encodeURIComponent(sessionPath);
    // Debug logs
    console.log('Session dropdown changed. sessionPath:', sessionPath);
    console.log('Encoded sessionPath:', encodedPath);

    // Clear and hide the image preview area before loading (new) images
    const previewWrapper = document.getElementById('imagePreview');
    const previewGrid = document.getElementById('imageGrid');
    if (previewGrid) previewGrid.innerHTML = '';
    if (previewWrapper) previewWrapper.style.display = 'none';

    // Initialise / reset Glightbox for image preview functionality
    if (window.glightbox) {
      window.glightbox.destroy();
    }
    window.glightbox = GLightbox({ selector: '.glightbox' });

    try {
      // Fetch session metadata based on selected session (path)
      console.log('Fetching /session-metadata?path=' + encodedPath);
      const res = await fetch(`/session-metadata?path=${encodedPath}`);
      if (!res.ok) throw new Error('Failed to fetch session metadata');
      const meta = await res.json();

      // Display session metadata in UI, with null checks
      const startedEl = document.getElementById("detail-started");
      if (startedEl) startedEl.textContent = meta.started || "-";
      const folderEl = document.getElementById("detail-folder");
      if (folderEl) folderEl.textContent = meta.folder || "-";
      const intervalEl = document.getElementById("detail-interval");
      if (intervalEl) intervalEl.textContent = meta.interval || "-";
      const imageCountEl = document.getElementById("detail-imagecount");
      if (imageCountEl) imageCountEl.textContent = meta.image_count ?? "-";

      // Load session images (thumbnail + dropdown + preview)
      await loadSessionImages(sessionPath);

      const sessionDetails = document.getElementById('sessionDetails');
      if (sessionDetails) sessionDetails.style.display = 'block';
    } catch (err) {
      console.error("Failed to fetch session metadata:", err);
      // Do not break UI, just hide session details
      const sessionDetails = document.getElementById('sessionDetails');
      if (sessionDetails) sessionDetails.style.display = 'none';
      return;
    }

    try {
      // Fetch and display images for the selected session
      console.log('Fetching /session-images?path=' + encodedPath);
      const imgRes = await fetch(`/session-images?path=${encodedPath}`);
      if (!imgRes.ok) throw new Error('Failed to fetch session images');
      const imgData = await imgRes.json();

      if (imgData.images && imgData.images.length > 0) {
        imgData.images.forEach(filename => {
          const link = document.createElement('a');
          link.href = `${sessionPath}/${filename}`;
          link.className = 'glightbox';
          link.setAttribute('data-gallery', 'session');

          const img = document.createElement('img');
          img.src = `${sessionPath}/${filename}`;
          img.alt = filename;
          img.style.height = '80px';
          img.style.cursor = 'pointer';

          link.appendChild(img);
          if (previewGrid) previewGrid.appendChild(link);
        });
        if (previewWrapper) previewWrapper.style.display = 'block';
      }
    } catch (err) {
      console.error("Failed to fetch session images:", err);
      // Don't break UI, just hide preview
      if (previewWrapper) previewWrapper.style.display = 'none';
    }
  });
});

// Loading the image in timelapse archive
async function loadSessionImages(folder) {
  const encodedPath = encodeURIComponent(folder);
  const previewWrapper = document.getElementById('imagePreview');
  const latestImageLink = document.getElementById('latestImageLink');
  const latestImage = document.getElementById('latestImage');
  const imageSelector = document.getElementById('imageSelector');
  const selectedImagePreview = document.getElementById('selectedImagePreview');
  const selectedImageLink = document.getElementById('selectedImageLink');
  const selectedImage = document.getElementById('selectedImage');

  try {
    const response = await fetch(`/session-images?path=${encodedPath}`);
    const imgData = await response.json();

    if (!imgData.images || imgData.images.length === 0) {
      previewWrapper.style.display = 'none';
      return;
    }

    previewWrapper.style.display = 'block';

    // Set latest image
    const latestFilename = imgData.images[imgData.images.length - 1];
    const latestImageUrl = `${folder}/${latestFilename}`;
    latestImageLink.href = latestImageUrl;
    latestImage.src = latestImageUrl;

    // Populate dropdown
    imageSelector.innerHTML = '';
    imgData.images.forEach(filename => {
      const option = document.createElement('option');
      option.value = filename;
      option.textContent = filename;
      imageSelector.appendChild(option);
    });

    // Set preview to first image by default
    const firstImage = imgData.images[0];
    if (firstImage) {
      const firstImageUrl = `${folder}/${firstImage}`;
      selectedImageLink.href = firstImageUrl;
      selectedImage.src = firstImageUrl;
      selectedImagePreview.style.display = 'block';
      imageSelector.value = firstImage;
    } else {
      selectedImagePreview.style.display = 'none';
    }

    // On dropdown change, update preview and lightbox link
    imageSelector.onchange = function () {
      const selectedFilename = this.value;
      if (selectedFilename) {
        const encodedPath = encodeURIComponent(folder);
        const selectedUrl = `${folder}/${selectedFilename}`;
        selectedImageLink.href = selectedUrl;
        selectedImage.src = selectedUrl;
        selectedImagePreview.style.display = 'block';
        if (window.glightbox) {
          window.glightbox.destroy();
        }
        window.glightbox = GLightbox({ selector: '.glightbox' });
      } else {
        selectedImagePreview.style.display = 'none';
      }
    };

    // Initialize or reload GLightbox
    if (window.glightbox) {
      window.glightbox.destroy();
    }
    window.glightbox = GLightbox({ selector: '.glightbox' });

  } catch (err) {
    console.error("Failed to load session images:", err);
    previewWrapper.style.display = 'none';
  }
}