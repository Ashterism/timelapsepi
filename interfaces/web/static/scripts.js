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
      document.getElementById("meta-timestamp").textContent = meta.timestamp || "unknown";
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

// Accordion logic
document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".accordion-button");
  buttons.forEach(button => {
    button.addEventListener("click", () => {
      const accordion = button.closest(".accordion");
      accordion.classList.toggle("open");
    });
  });
});

// Slide-out menu toggle
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
      document.getElementById("meta-timestamp").textContent = meta.timestamp || "unknown";
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
  const count = document.getElementById('end-count-input').value;
  const endTime = document.getElementById('end-time-input').value;
  const folder = document.getElementById('folder').value;

  const config = {
    interval,
    start_time: startTime || null,
    end_type: endType,
    count: endType === "count" ? parseInt(count) : null,
    end_time: endType === "time" ? endTime : null,
    folder: folder || null,
  };

  try {
    const res = await fetch('/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const text = await res.text();
    alert(text);
    fetchSessionInfo();
  } catch (err) {
    console.error("Error starting timelapse:", err);
    alert("❌ Failed to start timelapse.");
  }
}

async function stopTimelapse() {
  const res = await fetch('/stop', { method: 'POST' });
  const text = await res.text();
  alert(text);
  fetchSessionInfo();
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