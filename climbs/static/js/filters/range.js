// The Grade class is used to compare grades in filter_data_by_range()
// It is a wrapper class for the GRADES list
class Grade {
    constructor(grade) {
        this.grade_dict = GRADES.find(
            obj => obj[GRADE_SCALE] === grade
        );
        this.scale = GRADE_SCALE;
    }

    valueOf() {
        if (this.grade_dict === undefined)
            return NaN;
        return this.grade_dict.level;
    }
}

// Add a filter with a range
function add_filter_range(div, filter_key) {

    let filter = FILTERS[filter_key];
    div.addEventListener("change", filter_data_by_range);

    // Add the start and and end inputs
    for (let menu of ["start", "end"]) {

        // Add the options if the filter is a grade filter
        let input = null;
        if (filter.data_class == Grade) {
            input = document.createElement("select");
            for (let grade of GRADES) {
                let option = document.createElement("option");
                option.setAttribute("value", grade[GRADE_SCALE]);
                option.innerText = grade[GRADE_SCALE];
                input.appendChild(option);
            }
        }
        // Otherwise, the inputs are inputs, not dropdown menus
        else {
            input = document.createElement("input");
            if ("data_class" in filter && filter.data_class == Number)
                input.setAttribute("type", "number");
            else if ("data_class" in filter && filter.data_class == Date)
                input.setAttribute("type", "date");
            else
                input.setAttribute("type", "text");
        }
        input.setAttribute("class", menu + "-range");

        // If this is the end input, select the last option
        if (menu == "end") {
            // For grades, select the last grade
            if (filter.data_class == Grade)
                input.selectedIndex = input.options.length - 1;

            // For numbers, select the max. number
            if (filter.data_class == Number) {
                let max_value = 0;
                let is_float = false;
                for (let climb of DATA) {
                    let value = climb[filter.data_column];
                    if (value > max_value)
                        max_value = value;
                    if (value % 1 != 0)
                        is_float = true;
                }
                input.value = max_value;

                // If a float is found, set the step to 0.5
                if (is_float) {
                    input.setAttribute("step", "0.5");
                    range_div.getElementsByClassName(
                        "start-range"
                    )[0].setAttribute("step", "0.5");
                }
            }

            // For dates, select the last date
            if (filter.data_class == Date) {
                let max_date = new Date(0);
                for (let climb of DATA) {
                    let dates = climb[filter.data_column];
                    for (let date_str of dates) {
                        let date = new Date(date_str);
                        if (date > max_date)
                            max_date = date;
                    }
                }
                input.value = max_date.toISOString().substring(0, 10);
            }
        }
        div.appendChild(input);
    }
}

// Add the range filter and plot the data
// This function is called every time the range is changed
function filter_data_by_range(event) {

    // Get the selected range and the column
    let range_div = event.target.parentNode;
    let filter_key = range_div.dataset.column;
    let cls = FILTERS[filter_key].data_class;
    let attr = FILTERS[filter_key].data_column;

    let start_value = new cls(
        range_div.getElementsByClassName("start-range")[0].value
    );
    let end_value = new cls(
        range_div.getElementsByClassName("end-range")[0].value
    );

    // Find the column values that are within the selected range
    let selected_values = [];
    for (let climb of DATA) {
        // if climb[attr] is not a list (e.g. dates), convert it to a list
        values = climb[attr];
        if (!Array.isArray(values))
            values = [values];

        for (value_str of values) {
            let value = null;
            if (attr == "level") {
                let grade = GRADES.find(obj => obj["level"] === value_str);
                value = new cls(grade[GRADE_SCALE]);
            }
            else
                value = new cls(value_str);

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
    ACTIVE_FILTERS.set(attr, selected_values);
    plot_data();
}