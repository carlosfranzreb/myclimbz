function getTextWidth(text, obj) {
    let canvas = document.createElement("canvas");
    let context = canvas.getContext("2d");
    context.font = getComputedStyle(obj).font; // Use the button's font style
    let width = context.measureText(text).width;
    return width;
}

/* Constructs a filter widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {number} left - The left position of the widget
 */
var FilterWidget = function (id, left) {
    var self = this;
    self.left = left;
    self.id = id;
    wrapper = document.getElementById(id);
    wrapper.style.left = left + "px";
    wrapper.style.width = "fit-content";
    let inner_html =
        `<button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>Filter</button>` +
        `<div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>`;
    //add widgets here
    let cols = {};
    for (let filter_name in window.FILTERS) {
        let row = window.FILTERS[filter_name].row;
        let col = window.FILTERS[filter_name].col;
        if (col in cols) {
            if (row in cols[col]) {
                let filter_array = [cols[col][row]];
                filter_array.push(filter_name);
                cols[col][row] = filter_array;
            } else {
                cols[col][row] = filter_name;
            }
        } else {
            cols[col] = {};
            cols[col][row] = filter_name;
        }
    }
    wrapper.innerHTML = inner_html;

    let menu = document.getElementById(`${id}_menu`);
    let row = document.createElement("div");
    row.className = "row";
    row.id = `${id}_row`;

    for (let col in cols) {
        let colElement = document.createElement("div");
        colElement.className = "col";
        colElement.id = `${id}_col_${col}`;

        for (let row in cols[col]) {
            let filter_name = cols[col][row];
            if (filter_name instanceof Array) {
                let subrow = document.createElement("div");
                subrow.className = "row";
                subrow.id = `${id}_col_${col}_subrow_${row}`;
                for (let f of filter_name) {
                    let elem = document.createElement("div");
                    elem.id = `${id}_${f}`;
                    elem.innerHTML = f;
                    subrow.appendChild(elem);
                }
                colElement.appendChild(subrow);
            } else {
                let elem = document.createElement("div");
                elem.id = `${id}_${filter_name}`;
                elem.innerHTML = filter_name;
                colElement.appendChild(elem);
            }
        }

        row.appendChild(colElement);
    }

    menu.appendChild(row);

    let col_widths = [];
    menu.style.display = "block";
    let delta = 50;
    for (let filter_name in window.FILTERS) {
        let widget = window.FILTERS[filter_name]["filter_type"];
        let filter_id = `${id}_${filter_name}`;
        if (widget === "slider") {
            let step =
                "step" in window.FILTERS[filter_name]
                    ? window.FILTERS[filter_name]["step"]
                    : null;
            FILTER_WIDGETS.push(
                new DoubleRangeSlider(
                    filter_id,
                    filter_name.replace(/_/g, " "),
                    step,
                    window.FILTERS[filter_name]["data_class"],
                    window.FILTERS[filter_name]["data_column"]
                )
            );
        } else if (widget === "dropdown") {
            FILTER_WIDGETS.push(
                new DropdownMenu(
                    filter_id,
                    filter_name.replace(/_/g, " "),
                    window.FILTERS[filter_name]["data_column"]
                )
            );
        } else if (widget === "checkbox") {
            FILTER_WIDGETS.push(
                new Checkbox(
                    filter_id,
                    filter_name.replace(/_/g, " "),
                    window.FILTERS[filter_name]["data_column"]
                )
            );
        } else if (widget === "date_range") {
            FILTER_WIDGETS.push(
                new DateRange(
                    filter_id,
                    filter_name.replace(/_/g, " "),
                    window.FILTERS[filter_name]["data_column"]
                )
            );
        } else if (widget === "radio") {
            FILTER_WIDGETS.push(
                new RadioButton(
                    filter_id,
                    window.FILTERS[filter_name]["data_column"],
                    window.FILTERS[filter_name]["options"],
                    window.FILTERS[filter_name]["truth_values"]
                )
            );
        }
        let widgetWidth = Math.floor(
            FILTER_WIDGETS[FILTER_WIDGETS.length - 1].width
        );
        let current_col = window.FILTERS[filter_name]["col"];
        if (col_widths[current_col] === undefined) {
            col_widths[current_col] = widgetWidth + delta;
        } else {
            col_widths[current_col] = Math.max(
                col_widths[current_col],
                widgetWidth + delta
            );
        }
    }
    for (let w in col_widths) {
        let col = document.getElementById(`${id}_col_${w}`);
        col.style.width = `${col_widths[w]}px`;
    }

    for (let filter of FILTER_WIDGETS) {
        let filter_name = filter.id.split("_")[1];
        if (window.FILTERS[filter_name]["filter_type"] === "slider") {
            if (
                filter.width <
                col_widths[window.FILTERS[filter_name]["col"]] - delta
            ) {
                filter.adjust_width(
                    col_widths[window.FILTERS[filter_name]["col"]] - delta
                );
            }
        }
    }

    let divider = document.createElement("div");
    divider.className = "dropdown-divider";
    menu.appendChild(divider);

    let bottom_row = document.createElement("div");
    bottom_row.className = "row";
    bottom_row.id = `${id}_bottom_row`;

    let filter_apply = document.createElement("button");
    filter_apply.className = "btn btn-primary";
    filter_apply.id = "filter_apply";
    filter_apply.type = "button";
    filter_apply.innerHTML = "Apply";
    bottom_row.appendChild(filter_apply);

    let filter_reset = document.createElement("button");
    filter_reset.className = "btn btn-primary";
    filter_reset.id = "filter_reset";
    filter_reset.type = "button";
    filter_reset.innerHTML = "Reset";
    bottom_row.appendChild(filter_reset);

    menu.appendChild(bottom_row);

    self.menu = menu;

    self.menu.style.display = "none";
    let filter_button = document.getElementById(`${id}_button`);
    self.filter_button = filter_button;
    self.filter_button.addEventListener("click", openFilters);
    function openFilters() {
        self.menu.style.display =
            self.menu.style.display === "block" ? "none" : "block";
    }

    // Reset all filters when the reset button is clicked
    filter_reset.addEventListener("click", function () {
        if (DATA.length === 0) {
            return;
        }
        for (let i = 0; i < FILTER_WIDGETS.length; i++) {
            FILTER_WIDGETS[i].reset();
        }
    });

    // Apply filters when the apply button is clicked
    filter_apply.addEventListener("click", function () {
        display_data();
        self.menu.style.display = "none";
    });

    document.addEventListener("click", function (event) {
        // if the user clicks outside of the filter widget, and no widget inside it is in focus, close the filter widget
        if (
            !wrapper.contains(event.target) &&
            document.activeElement.tagName === "BODY"
        ) {
            self.menu.style.display = "none";
        }
    });
};
