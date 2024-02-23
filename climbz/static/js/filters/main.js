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

let FILTER_WIDGETS = [];

// --- List of available filters and their corresponding functions
FILTERS = {
    "Grade": {
        "filter_type": "slider",
        "data_class": Grade,
        "data_column": "level",
        "row": 0,
        "col": 0,
    },
    //"Date": {
    //    "filter_type": "range",
    //    "data_class": Date,
    //    "data_column": "dates",
    //    "row": 0,
    //    "col": 0,
    //},
    "Inclination": {
        "filter_type": "slider",
        "data_class": Number,
        "step": 5, 
        "data_column": "inclination",
        "row": 1,
        "col": 0,
    },
    "Landing": {
        "filter_type": "slider",
        "data_class": Number,
        "step": 1, 
        "data_column": "landing",
        "row": 0,
        "col": 1,
    },
    "Attempts": {
        "filter_type": "slider",
        "data_class": Number,
        "step": 1, 
        "data_column": "n_attempts_send",
        "row": 1,
        "col": 1,
    },
    "Height": {
        "filter_type": "slider",
        "data_class": Number,
        "step": 0.5, 
        "data_column": "height",
        "row": 2,
        "col": 1,
        "is_float": true,
    },
    "Area": {
        "filter_type": "dropdown",
        "data_column": "area",
        "row": 2,
        "col": 0,
    },
    "Crux": {
        "filter_type": "dropdown",
        "data_column": "cruxes",
        "row": 3,
        "col": 1,
    },
    //"Sit_start": {
    //    "filter_type": "checkbox",
    //    "row": 3,
    //    "col": 0,
    //},
    //"Projects": {
    //    "filter_type": "checkbox",
    //    "row": 3,
    //    "col": 0,
    //},
    "Sends": {
        "filter_type": "checkbox",
        "data_column": "sent",
        "false_value": false, 
        "row": 3,
        "col": 0,
    },
    "Attempted": {
        "filter_type": "checkbox",
        "data_column": "n_sessions",
        "false_value": 0, 
        "row": 4,
        "col": 0,
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
    if (FILTER_WIDGETS.length === 0)
        return this_data;

    // Apply the active filters
    let filtered_data = [];
    for (let climb of this_data) {
        let include = false;
        for (let w of FILTER_WIDGETS) {
            include = w.filter_value(climb[w.data_column]);
            //TODO: Clear this
            if (!include)
                break;
        }
        if (include)
            filtered_data.push(climb);
    }
    return filtered_data;
}