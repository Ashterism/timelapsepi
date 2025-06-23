let lastTimestamp = null;

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

function resetButton(btn) {
  btn.disabled = false;
  btn.textContent = "Take Test Photo";
}