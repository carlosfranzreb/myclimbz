// Add a filter with a list of checkboxes to select options, and a button to
// select all options.
function add_filter_checkboxes(div, column) {

    // Add the multiple-choice selection menu
    let menu_div = document.createElement("div");
    menu_div.setAttribute("class", "select-multiple");
    menu_div.addEventListener("change", filter_data_by_checkboxes);
    div.appendChild(menu_div);

    // Get the values from DATA, and add "All" as an option
    let data_column = FILTERS[column].data_column;
    let values = new Set();
    for (let climb of DATA) {
        // if climb[data_column] is not a list (e.g. dates), convert it to a list
        let climb_values = climb[data_column];
        if (!Array.isArray(climb_values))
            climb_values = [climb_values];
        for (let value of climb_values)
            values.add(value);
    }
    values = Array.from(values).sort();
    values.unshift("All");

    // Add the values to the dropdown menu
    for (let value of values) {
        let checkbox = document.createElement("input");
        checkbox.setAttribute("type", "checkbox");
        checkbox.setAttribute("value", value);
        checkbox.checked = true;
        let option = document.createElement("label");
        option.innerHTML = value;
        option.appendChild(checkbox);
        menu_div.appendChild(option);
    }

    // Attrs to keep track of whether "All" was selected and the column name
    menu_div.setAttribute("data-all_clicked", "true");
    menu_div.setAttribute("data-column", column);
}


// Add the checkbox filters and plot the data if options are selected
// This function is called every time a checkbox is checked or unchecked
function filter_data_by_checkboxes(event) {

    // Get the column and selected options
    let clicked_checkbox = event.target;
    let filter_div = event.target.parentNode.parentNode;
    let column = FILTERS[filter_div.dataset.column].data_column;
    let selected_options = Array.from(filter_div.querySelectorAll("input:checked"))
        .map(function (checkbox) {
            return checkbox.value;
        });

    // If "All" was selected before, and another option is clicked
    // check only the clicked option
    if (filter_div.dataset.all_clicked == "true" && clicked_checkbox.value != "All") {
        filter_div.dataset.all_clicked = "false";
        for (let checkbox of filter_div.querySelectorAll("input"))
            checkbox.checked = false;
        clicked_checkbox.checked = true;
        ACTIVE_FILTERS.set(column, []);
        ACTIVE_FILTERS.get(column).push(clicked_checkbox.value);
    }

    else {
        // If "All" is selected, check all options and add the filter
        if (selected_options.includes("All")) {
            for (let checkbox of filter_div.querySelectorAll("input"))
                checkbox.checked = true;
            let all_options = Array.from(filter_div.querySelectorAll("input"))
                .map(function (checkbox) {
                    return checkbox.value;
                });
            ACTIVE_FILTERS.set(column, all_options);
            filter_div.dataset.all_clicked = true;
            selected_options = selected_options.filter(option => option != "All");
        }

        // Otherwise, add the filter with the selected options
        else
            ACTIVE_FILTERS.set(column, selected_options);
    }

    display_data();
}