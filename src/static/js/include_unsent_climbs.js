// Retrieve the checkbox element
let unsent_climbs_btn = document.getElementById("include-unsent-climbs");

// Add an event listener to the checkbox
unsent_climbs_btn.addEventListener("change", function() {
    INCLUDE_UNSENT_CLIMBS = unsent_climbs_btn.checked;
    console.log(INCLUDE_UNSENT_CLIMBS);
    plot_data();
});