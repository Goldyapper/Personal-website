// Make filterByLine globally accessible
function filterByLine() {
    const selectedLine = document.getElementById('line-filter').value;
    const sections = document.querySelectorAll('.platform-section');

    sections.forEach(section => {
        const line = section.getAttribute('data-line');
        if (selectedLine === 'all' || line === selectedLine) {
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    });
}

// DOM ready setup
document.addEventListener("DOMContentLoaded", function () {
    const dropdown = document.querySelector('.station-select');
    if (dropdown) {
        $(dropdown).select2({
            width: '100%',
            placeholder: "Select a station"
        });
    }
});
