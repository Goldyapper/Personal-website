document.addEventListener("DOMContentLoaded", function() {
    const dropdown = document.querySelector('.station-select');
    if (dropdown) {
        $(dropdown).select2({
            width: '100%',
            placeholder: "Select a station"
        });
    }
});
