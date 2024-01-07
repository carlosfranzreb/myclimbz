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
}

// Add a filter to the list of filters
function add_filter() {
    let filter_list = document.getElementById("filterList");
    let filter_container = document.createElement("div");
    filter_container.classList.add("filter-container");

    // add dropdown menu to select filter
    let filter_selection = document.createElement("select");
    for (let option of Object.keys(FILTERS)) {
        if (ACTIVE_FILTERS.has(FILTERS[option].data_column))
            continue;
        else
            filter_selection.options.add(new Option(option, option));
    }
    filter_selection.addEventListener("change", change_filter);
    filter_container.appendChild(filter_selection);

    // add dropdown menu to select filter value
    let selected = filter_selection.options[filter_selection.selectedIndex].value;
    let filter_div = document.createElement("div");
    create_filter(filter_div, selected);
    filter_container.appendChild(filter_div);

    // add remove button to container
    let remove_button = document.createElement("button");
    remove_button.innerText = "Remove";
    remove_button.addEventListener("click", remove_filter);
    filter_container.appendChild(remove_button);

    // add container to list
    filter_list.appendChild(filter_container);
}

function create_filter(div, filter_key) {
    div.classList.add("filter_div");
    div.dataset.column = filter_key;
    let filter_type = FILTERS[filter_key]["filter_type"];
    if (filter_type == "range")
        add_filter_range(div, filter_key);
    else if (filter_type == "checkboxes")
        add_filter_checkboxes(div, filter_key);
}


// Change the filter options when a new filter is selected
function change_filter(event) {

    // get the filter container and the old and new selected filters
    let filter_container = event.target.parentNode;
    let filter_div = filter_container.querySelector(".filter_div");
    let old_selected_option = filter_div.dataset.column;
    let selected_option = event.target.options[event.target.selectedIndex].value;

    // remove the filter from the list of active filters
    ACTIVE_FILTERS.delete(FILTERS[old_selected_option].data_column);

    // add new filter and remove the old one
    let new_filter_div = document.createElement("div");
    create_filter(new_filter_div, selected_option);

    filter_container.insertBefore(new_filter_div, filter_div);
    filter_container.removeChild(filter_div);
    display_data();
}


// Remove a filter from the list of filters
function remove_filter(event) {

    // remove the filter from the list of active filters and plot the data
    let filter_container = event.target.parentNode;
    let select_menu = filter_container.querySelector("select")
    let selected_option = select_menu.options[select_menu.selectedIndex].value;
    ACTIVE_FILTERS.delete(FILTERS[selected_option].data_column);

    // remove the filter from the list of filters
    let filter_list = filter_container.parentNode;
    filter_list.removeChild(filter_container);

    display_data();
}


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
        let include = true;
        for (let [filter_key, filter_value] of ACTIVE_FILTERS) {
            let climb_values = climb[filter_key];
            if (!Array.isArray(climb_values))
                climb_values = [climb_values];
            for (let climb_value of climb_values) {
                if (!filter_value.includes(climb_value)) {
                    include = false;
                    break;
                }
            }
            if (!include)
                break;
        }
        if (include)
            filtered_data.push(climb);
    }
    return filtered_data;
}