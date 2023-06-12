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

    // Get the values from DATA
    let values = new Set();
    for (let climb of DATA)
        values.add(climb["Area"]);

    // Add the values to the dropdown menu
    for (let value of Array.from(values).sort()) {
        let checkbox = document.createElement("input");
        checkbox.setAttribute("type", "checkbox");
        checkbox.setAttribute("value", value);
        let option = document.createElement("label");
        option.innerHTML = value;
        option.appendChild(checkbox);
        menu_div.appendChild(option);
    }
}


// Add the area filters and plot the data if options are selected
function filter_data_by_area() {
    let select = document.getElementById("area-select");
    let selected_options = Array.from(select.querySelectorAll("input[type='checkbox']:checked"))
        .map(function(checkbox) {
            return checkbox.value;
        });
    if (selected_options.length == 0)
        ACTIVE_FILTERS.delete("Area");
    else {
        ACTIVE_FILTERS.set("Area", selected_options);
        plot_data();
    }
}