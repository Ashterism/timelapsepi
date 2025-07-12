// This script handles taking a new photo and updating the preview image

let lastTimestamp = null;

// Called when the "Take Test Photo" button is clicked
// Disables the button, fetches a new photo, and waits for an updated timestamp
async function takePhoto() {
  const btn = document.querySelector('button[onclick="takePhoto()"]');
  btn.disabled = true;
  btn.textContent = "📸 Taking...";

  try {
    console.log("⏳ Fetching latest timestamp...");
    const res = await fetch('/photo/latest-timestamp');
    console.log("📸 Timestamp fetch status:", res.status);
    lastTimestamp = await res.text();

    console.log("⏳ Sending photo request...");
    const photoRes = await fetch('/photo/photo', { method: 'POST' });
    console.log("📸 Photo fetch status:", photoRes.status);
    if (!photoRes.ok) throw new Error('Photo failed');

    setTimeout(() => pollForNewPhoto(btn), 1000);
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
