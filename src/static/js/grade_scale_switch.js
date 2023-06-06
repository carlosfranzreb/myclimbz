// Retrieve the checkbox element
let customAxisToggle = document.getElementById("grade-scale-toggle");

// Add an event listener to the checkbox
customAxisToggle.addEventListener("change", function() {
    let is_checked = customAxisToggle.checked;
    GRADE_SCALE = is_checked ? "hueco" : "font";
    plot_data();
});