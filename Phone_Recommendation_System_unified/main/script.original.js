// Add event listeners for icons for interaction
document.querySelectorAll(".icon-box").forEach(icon => {
    icon.addEventListener("click", function() {
        alert("You clicked on: " + this.querySelector("p").innerText);
    });
});
