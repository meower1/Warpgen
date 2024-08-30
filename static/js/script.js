document.addEventListener("DOMContentLoaded", async () => {
  const keyBox = document.getElementById("subscription-key");
  const copyButton = document.getElementById("copy-button");
  const copyText = document.getElementById("copy-text");
  const checkIcon = document.getElementById("check-icon");
  const refreshButton = document.getElementById("refresh-button");

  // Fetch the subscription key from the FastAPI endpoint
  try {
    const response = await fetch("/api/"); // Adjusted path for Vercel
    if (response.ok) {
      let key = await response.text(); // Assuming the response is plain text
      key = key.replace(/['"]+/g, ""); // Remove surrounding quotation marks
      keyBox.textContent = key;
    } else {
      keyBox.textContent = "Error fetching key";
    }
  } catch (error) {
    keyBox.textContent = "Error fetching key";
  }

  // Copy to clipboard functionality
  copyButton.addEventListener("click", () => {
    const key = keyBox.textContent;
    navigator.clipboard
      .writeText(key)
      .then(() => {
        // Show checkmark icon
        copyText.style.display = "none";
        checkIcon.style.display = "block";

        // Revert back after 1 second
        setTimeout(() => {
          copyText.style.display = "block";
          checkIcon.style.display = "none";
        }, 1000);
      })
      .catch((err) => {
        console.error("Failed to copy: ", err);
      });
  });

  // Refresh page functionality
  refreshButton.addEventListener("click", () => {
    location.reload();
  });
});
