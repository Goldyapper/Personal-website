// Make filterByLine globally accessible
function filterByLine() {
    const selectedLine = document.getElementById('line-filter').value.toLowerCase();
    const sections = document.querySelectorAll('.platform-section');

    sections.forEach(section => {
        const lines = section.getAttribute('data-line').toLowerCase().split(',').map(s => s.trim());
        if (selectedLine === 'all' || lines.includes(selectedLine)) {
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
