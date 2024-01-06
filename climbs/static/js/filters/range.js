// The Grade class is used to compare grades in filter_data_by_range()
// It is a wrapper class for the GRADES list
class Grade {
    constructor(grade) {
        this.grade_dict = GRADES.find(
            obj => obj[GRADE_SCALE] === grade
        );
        this.scale = GRADE_SCALE;
    }
}

Grade.prototype.valueOf = function () {
    if (this.grade_dict === undefined)
        return NaN;
    return this.grade_dict.level;
}

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
    let column_attr = FILTER_ATTRS[column_str];

    let start_value = new column_cls(
        range_div.getElementsByClassName("start-range")[0].value
    );
    let end_value = new column_cls(
        range_div.getElementsByClassName("end-range")[0].value
    );

    // Find the column values that are within the selected range
    let selected_values = [];
    for (let climb of DATA) {
        // if climb[column_attr] is not a list (e.g. dates), convert it to a list
        values = climb[column_attr];
        if (!Array.isArray(values))
            values = [values];

        for (value_str of values) {
            let value = null;
            if (column_attr == "level") {
                grade = GRADES.find(obj => obj["level"] === value_str);
                value = new column_cls(grade[GRADE_SCALE]);
            }
            else
                value = new column_cls(value_str);

            if (isNaN(value))
                continue;
            if (!isNaN(start_value) && value < start_value)
                continue;
            if (!isNaN(end_value) && value > end_value)
                continue;
            if (!selected_values.includes(value_str))
                selected_values.push(value_str);
        }
    }

    // Add the filter
    ACTIVE_FILTERS.set(column_attr, selected_values);
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


// Function called by add_filter_range to create the range filter for this column.
// It returns a div with two number inputs, one for the start and one for the end.
// The start input must have the class "start-range" and the end input must have
// the class "end-range".
function get_filter_range_tries() {

    let div = document.createElement("div");

    // Add the start- and end-range inputs
    for (let menu of ["start", "end"]) {
        let tries_input = document.createElement("input");
        tries_input.setAttribute("type", "number");
        tries_input.setAttribute("class", menu + "-range");

        // If this is the end-range input, set it to the the max. number of tries
        if (menu == "end") {
            let max_tries = 0;
            for (let climb of DATA) {
                let tries = new Tries(climb["Tries"]);
                if (tries > max_tries)
                    max_tries = tries;
            }
            tries_input.value = max_tries;
        }

        div.appendChild(tries_input);
    }

    return div;
}
