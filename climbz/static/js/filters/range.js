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
        }
        input.setAttribute("class", menu + "-range");

        // If the filter is about floats, add the step attribute
        if ("is_float" in filter && filter.is_float)
            input.setAttribute("step", "0.5");

        // Define a comparison function based on the menu
        function get_comparison_function(menu) {
            if (menu === "start")
                return (value, minValue) => value < minValue;
            else if (menu === "end")
                return (value, maxValue) => value > maxValue;
        }

        // Select the min. and max. values for the inputs

        // For grades, select the last grade
        if (filter.data_class === Grade) {
            let option = menu === "start" ? 0 : input.options.length - 1;
            input.selectedIndex = option;
        }

        // For numbers and dates, select the min. or max. value
        if (filter.data_class === Number || filter.data_class === Date) {
            let compare_func = get_comparison_function(menu);
            let extreme;
            if (filter.data_class === Number)
                extreme = menu === "start" ? Number.MAX_SAFE_INTEGER : 0;
            else if (filter.data_class === Date)
                extreme = menu === "start" ? new Date(8640000000000000) : new Date(0);

            for (let climb of DATA) {
                let values = climb[filter.data_column];
                if (!Array.isArray(values))
                    values = [values];

                for (let valueStr of values) {
                    let value = new filter.data_class(valueStr);
                    if (compare_func(value, extreme))
                        extreme = value;
                }
            }
            input.value = extreme;
            if (filter.data_class === Date)
                input.value = extreme.toISOString().substring(0, 10);
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
    display_data();
}