// Retrieve the checkbox element
let grade_scale_toggle = document.getElementById("grade-scale-toggle");

// Add an event listener to the checkbox
grade_scale_toggle.addEventListener("change", function() {
    GRADE_SCALE = grade_scale_toggle.checked ? "hueco" : "font";
    plot_data();
});