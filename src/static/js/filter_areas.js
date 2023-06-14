// Add an area filter: options are shown alphabetically,
// and multiple options can be selected
function add_area_filter(div) {

    // Add the multiple-choice selection menu
    let menu_div = document.createElement("div");
    menu_div.setAttribute("id", "area-select");
    menu_div.setAttribute("class", "select-multiple");
    menu_div.setAttribute("onchange", "filter_data_by_area()");
    // select.setAttribute("data-mdb-placeholder", "Select areas");
    div.appendChild(menu_div);

    // Get the values from DATA, and add "All" as an option
    let values = new Set();
    for (let climb of DATA)
        values.add(climb["Area"]);
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

    // Add an attribute to the menu to keep track of whether "All" was selected
    // (this is used in filter_data_by_area())
    menu_div.setAttribute("all-clicked", "true");
}


// Add the area filters and plot the data if options are selected
// This function is called every time a checkbox is checked or unchecked
function filter_data_by_area() {


    // Get the selected options
    let select = document.getElementById("area-select");
    let selected_options = Array.from(select.querySelectorAll("input:checked"))
        .map(function(checkbox) {
            return checkbox.value;
        });
    
    // If "All" was selected before, and is not selected anymore, uncheck all
    if (select.getAttribute("all-clicked") == "true" && !("All" in selected_options)) {
        select.setAttribute("all-clicked", "false");
        for (let checkbox of select.querySelectorAll("input"))
            checkbox.checked = false;
        
        ACTIVE_FILTERS.set("Area", []);
    }

    else {
        // If "All" is selected, check all options and add the filter
        if (selected_options.includes("All")) {
            for (let checkbox of select.querySelectorAll("input"))
                checkbox.checked = true;
            let all_options = Array.from(select.querySelectorAll("input"))
                .map(function(checkbox) {
                    return checkbox.value;
                });
            ACTIVE_FILTERS.set("Area", all_options);
            select.setAttribute("all-clicked", "true");
            selected_options = selected_options.filter(option => option != "All");
        }

        // Otherwise, add the filter with the selected options
        else
            ACTIVE_FILTERS.set("Area", selected_options);
    }

    plot_data();
}