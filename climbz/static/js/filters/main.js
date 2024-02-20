// --- Buttons at the top of the page

// Add an event listener to the checkbox "Include unsent climbs"
let unsent_climbs_btn = document.getElementById("include-unsent-climbs");
unsent_climbs_btn.addEventListener("change", function () {
    INCLUDE_UNSENT_CLIMBS = unsent_climbs_btn.checked;
    display_data();
});


// Add an event listener to the checkbox "Grade scale"
let grade_scale_toggle = document.getElementById("grade-scale-toggle");
grade_scale_toggle.addEventListener("change", function () {
    GRADE_SCALE = grade_scale_toggle.checked ? "hueco" : "font";
    display_data();
});


// --- List of available filters and their corresponding functions
FILTERS = {
    "Grade": {
        "filter_type": "range",
        "data_class": Grade,
        "data_column": "level",
    },
    "Date": {
        "filter_type": "range",
        "data_class": Date,
        "data_column": "dates",
    },
    "Inclination": {
        "filter_type": "range",
        "data_class": Number,
        "data_column": "inclination",
    },
    "Landing": {
        "filter_type": "range",
        "data_class": Number,
        "data_column": "landing",
    },
    "Attempts": {
        "filter_type": "range",
        "data_class": Number,
        "data_column": "n_attempts_send",
    },
    "Height": {
        "filter_type": "range",
        "data_class": Number,
        "data_column": "height",
        "is_float": true,
    },
    "Area": {
        "filter_type": "checkboxes",
        "data_column": "area",
    },
    "Crux": {
        "filter_type": "checkboxes",
        "data_column": "cruxes",
    },
};


// Filter the global data according to the active filters
function filter_data() {

    // Remove unsent climbs if the corresponding button is unchecked
    let this_data = null;
    if (INCLUDE_UNSENT_CLIMBS)
        this_data = DATA;
    else
        this_data = DATA.filter(d => d.sent === true);

    // Apply the active filters
    let filtered_data = [];
    for (let climb of this_data) {
        let include = ACTIVE_FILTERS.size == 0;
        for (let [filter_key, filter_value] of ACTIVE_FILTERS) {
            let climb_values = climb[filter_key];
            if (!Array.isArray(climb_values))
                climb_values = [climb_values];
            for (let climb_value of climb_values) {
                if (filter_value.includes(climb_value)) {
                    include = true;
                    break;
                }
            }
            if (include)
                break;
        }
        if (include)
            filtered_data.push(climb);
    }
    return filtered_data;
}