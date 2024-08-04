// If the width is below 800px, show only 3 columns. Always show the first two
// columns. If the last column header says "Actions", show it. Otherwise, show
// the third column.
function hide_columns() {
    if (window.innerWidth < 800) {
        // load the table and get its last header
        let table = window.data_table;
        let n_cols = table.columns.size();
        let last_header = table.dom.querySelectorAll(
            "thead tr th"
        )[n_cols - 1].textContent

        // hide columns based on the last header
        let hide_indices = [...Array(n_cols).keys()].slice(2);
        if (last_header !== "Actions")
            hide_indices = hide_indices.slice(1);
        else
            hide_indices = hide_indices.slice(0, -1);
        table.columns.hide((hide_indices));
    }
}

// Add the event listener to the window
window.addEventListener("resize", hide_columns);
window.addEventListener("load", hide_columns);