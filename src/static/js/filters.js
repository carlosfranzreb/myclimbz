// Functions related to filtering the data

// List of available filters
FILTERS = {
    // "Grade",
    "Area": add_area_filter,
    // "Inclination",
    // "Landing",
    // "Date",
    // "Tries",
    // "Sit start",
    // "Height",
    // "Style",
}


// Add a filter to the list of filters
function add_filter() {
    let filter_list = document.getElementById("filterList");
    let filter_container = document.createElement("div");
    filter_container.classList.add("filter-container");

    // add dropdown menu to select filter
    let filter_selection = document.createElement("select");
    for (let option of Object.keys(FILTERS))
        filter_selection.options.add(new Option(option, option));
    filter_container.appendChild(filter_selection);

    // add dropdown menu to select filter value
    let selected = filter_selection.options[filter_selection.selectedIndex].value;
    let filter_options = document.createElement("div");
    FILTERS[selected](filter_options);
    filter_container.appendChild(filter_options);

    // add remove button to container
    let remove_button = document.createElement("button");
    remove_button.innerText = "Remove";
    remove_button.onclick = function() {
        filter_list.removeChild(filter_container);
        ACTIVE_FILTERS.delete(selected);
        plot_data();
    };
    filter_container.appendChild(remove_button);

    // add container to list
    filter_list.appendChild(filter_container);
}
