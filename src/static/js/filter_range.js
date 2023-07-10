// Add a filter with a range
function add_filter_range(div, column) {

    // Add the start and and end inputs
    let range_div = eval("get_filter_range_" + column.toLowerCase() + "()");
    range_div.setAttribute("data-column", column);
    range_div.addEventListener("change", filter_data_by_range);
    div.appendChild(range_div);
}


// Add the range filter and plot the data
// This function is called every time the range is changed
function filter_data_by_range(event) {

    // Get the selected range and the column
    let range_div = event.target.parentNode;
    let column_str = range_div.dataset.column;
    let column_cls = eval(column_str);
    let start_value = new column_cls(range_div.getElementsByClassName("start-range")[0].value);
    let end_value = new column_cls(range_div.getElementsByClassName("end-range")[0].value);

    // Find the column values that are within the selected range
    let selected_values = [];
    for (let climb of DATA) {
        let value = new column_cls(climb[column_str]);
        if (isNaN(value))
            continue;
        if (! isNaN(start_value) && value < start_value)
            continue;
        if (! isNaN(end_value) && value > end_value)
            continue;
        selected_values.push(climb[column_str]);
    }

    // Add the filter
    ACTIVE_FILTERS.set(column_str, selected_values);
    plot_data();
}


// Function called by add_filter_range to create the range filter for this column
// It returns a div with the start and end dropdown menus, filled with grades, and
// with the min and max grades selected.
// The start input must have the class "start-range" and the end input must have
// the class "end-range".
function get_filter_range_grade() {

    let div = document.createElement("div");

    // Add the start- and end-grade inputs
    for (let menu of ["start", "end"]) {
        let grade_select = document.createElement("select");
        grade_select.setAttribute("class", menu + "-range");

        // Add the options
        for (let grade of GRADES) {
            let option = document.createElement("option");
            option.setAttribute("value", grade[GRADE_SCALE]);
            option.innerText = grade[GRADE_SCALE];
            grade_select.appendChild(option);
        }

        // If this is the end-grade input, select the last grade
        if (menu == "end")
            grade_select.selectedIndex = grade_select.options.length - 1;

        div.appendChild(grade_select);
    }

    return div;
}


// Function called by add_filter_range to create the range filter for this column.
// It returns a div with two date inputs, one for the start and one for the end.
// The start input must have the class "start-range" and the end input must have
// the class "end-range".
function get_filter_range_date() {

    let div = document.createElement("div");

    // Add the start- and end-grade inputs
    for (let menu of ["start", "end"]) {
        let date_input = document.createElement("input");
        date_input.setAttribute("type", "date");
        date_input.setAttribute("class", menu + "-range");

        div.appendChild(date_input);
    }

    return div;
}