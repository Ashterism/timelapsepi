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
});

document.addEventListener("DOMContentLoaded", function () {
  fetch('/status')
    .then(response => response.json())
    .then(data => {
      document.getElementById("battery-status").textContent = `${data.battery_level}% (${data.power_source})`;
      document.getElementById("connection-status").textContent = data.wifi_mode === "hotspot" ? "Hotspot" : "Wi-Fi";
    })
    .catch(err => {
      document.getElementById("battery-status").textContent = "Unavailable";
      document.getElementById("connection-status").textContent = "Unavailable";
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
