// This script handles taking a new photo and updating the preview image

let lastTimestamp = null;

// Called when the "Take Test Photo" button is clicked
// Disables the button, fetches a new photo, and waits for an updated timestamp
async function takePhoto() {
  const btn = document.querySelector('button[onclick="takePhoto()"]');
  btn.disabled = true;
  btn.textContent = "📸 Taking...";

  try {
    const res = await fetch('/latest-timestamp');
    lastTimestamp = await res.text();

    const photoRes = await fetch('/photo');
    if (!photoRes.ok) throw new Error('Photo failed');

    setTimeout(() => pollForNewPhoto(btn), 1000);
  } catch (err) {
    console.error(err);
    alert('❌ Error taking photo.');
    resetButton(btn);
  }
}

// Polls the server every second until the timestamp changes, indicating a new photo is available
function pollForNewPhoto(btn) {
  fetch('/latest-timestamp')
    .then(res => res.text())
    .then(newTimestamp => {
      if (newTimestamp !== lastTimestamp) {
        document.getElementById('photo').src = `/latest.jpg?${Date.now()}`;
        resetButton(btn);
      } else {
        setTimeout(() => pollForNewPhoto(btn), 1000);
      }
    })
    .catch(() => resetButton(btn));
}

// Resets the button state after photo has been updated or if an error occurs
function resetButton(btn) {
  btn.disabled = false;
  btn.textContent = "Take Test Photo";
}

// Accordion logic
document.addEventListener("DOMContentLoaded", function () {
  const buttons = document.querySelectorAll(".accordion-button");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.classList.toggle("active");
      const content = btn.nextElementSibling;
      content.style.display = content.style.display === "block" ? "none" : "block";
    });
  });
});