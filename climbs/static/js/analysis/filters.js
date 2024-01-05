// --- Buttons at the top of the page


// Add an event listener to the checkbox "Include unsent climbs"
let unsent_climbs_btn = document.getElementById("include-unsent-climbs");
unsent_climbs_btn.addEventListener("change", function() {
    INCLUDE_UNSENT_CLIMBS = unsent_climbs_btn.checked;
    plot_data();
});


// Add an event listener to the checkbox "Grade scale"
let grade_scale_toggle = document.getElementById("grade-scale-toggle");
grade_scale_toggle.addEventListener("change", function() {
    GRADE_SCALE = grade_scale_toggle.checked ? "hueco" : "font";
    plot_data();
});


// --- List of available filters and their corresponding functions
FILTERS = {
    "Grade": add_filter_range,
    "Area": add_filter_checkboxes,
    "Inclination": add_filter_checkboxes,
    "Landing": add_filter_checkboxes,
    "Date": add_filter_range,
    "Tries": add_filter_range,
    "Sit start": add_filter_checkboxes,
    "Height": add_filter_checkboxes,
    "Style": add_filter_checkboxes,
}


// Add a filter to the list of filters
function add_filter() {
    let filter_list = document.getElementById("filterList");
    let filter_container = document.createElement("div");
    filter_container.classList.add("filter-container");

    // add dropdown menu to select filter
    let filter_selection = document.createElement("select");
    for (let option of Object.keys(FILTERS)) {
        if (ACTIVE_FILTERS.has(option))
            continue;
        else
            filter_selection.options.add(new Option(option, option));
    }
    filter_selection.addEventListener("change", change_filter);
    filter_container.appendChild(filter_selection);

    // add dropdown menu to select filter value
    let selected = filter_selection.options[filter_selection.selectedIndex].value;
    let filter_div = document.createElement("div");
    filter_div.classList.add("filter_div");
    FILTERS[selected](filter_div, selected);
    filter_container.appendChild(filter_div);

    // add remove button to container
    let remove_button = document.createElement("button");
    remove_button.innerText = "Remove";
    remove_button.addEventListener("click", remove_filter);
    filter_container.appendChild(remove_button);

    // add container to list
    filter_list.appendChild(filter_container);
}


// Change the filter options when a new filter is selected
function change_filter(event) {

    // get the filter container and the old and new selected filters
    let filter_container = event.target.parentNode;
    let filter_div = filter_container.querySelector(".filter_div");
    let old_selected_option = filter_div.querySelector("div").dataset.column;
    let selected_option = event.target.options[event.target.selectedIndex].value;

    // remove the filter from the list of active filters
    ACTIVE_FILTERS.delete(old_selected_option);

    // add new filter and remove the old one
    let new_filter_div = document.createElement("div");
    new_filter_div.classList.add("filter_div");
    FILTERS[selected_option](new_filter_div, selected_option);
    filter_container.insertBefore(new_filter_div, filter_div);
    filter_container.removeChild(filter_div);

    plot_data();
}


// Remove a filter from the list of filters
function remove_filter(event) {

    // remove the filter from the list of active filters and plot the data
    let filter_container = event.target.parentNode;
    let select_menu = filter_container.querySelector("select")
    let selected_option = select_menu.options[select_menu.selectedIndex].value;
    ACTIVE_FILTERS.delete(selected_option);
    plot_data();

    // remove the filter from the list of filters
    let filter_list = filter_container.parentNode;
    filter_list.removeChild(filter_container);
}