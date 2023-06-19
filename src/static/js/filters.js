// Functions related to filtering the data

// List of available filters
FILTERS = {
    // "Grade",
    "Area": add_filter_checkboxes,
    "Inclination": add_filter_checkboxes,
    "Landing": add_filter_checkboxes,
    // "Date",
    // "Tries",
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
    let filter_options = document.createElement("div");
    FILTERS[selected](filter_options, selected);
    filter_container.appendChild(filter_options);

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
    let filter_options = filter_container.querySelector("div");
    let old_selected_option = filter_options.dataset.column;
    let selected_option = event.target.options[event.target.selectedIndex].value;

    // remove old filter options and the filter from the list of active filters
    console.log(old_selected_option);
    ACTIVE_FILTERS.delete(old_selected_option);
    plot_data();
    filter_container.removeChild(filter_options);
    console.log(ACTIVE_FILTERS);

    // add new filter options
    filter_options = document.createElement("div");
    FILTERS[selected_option](filter_options, selected_option);
    filter_container.insertBefore(filter_options, filter_container.childNodes[1]);
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