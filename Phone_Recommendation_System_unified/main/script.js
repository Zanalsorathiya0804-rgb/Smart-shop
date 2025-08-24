
// Open module URL when icon clicked. Make sure module servers are running.
document.querySelectorAll(".icon-box").forEach(icon => {
    icon.style.cursor = "pointer";
    icon.addEventListener("click", function() {
        const url = this.getAttribute("data-url") || null;
        if (!url || url === "#") {
            alert("Module URL not configured.");
            return;
        }
        // open in a new tab. Change to window.location.href = url to open in same tab.
        window.open(url, "_blank");
    });
});
