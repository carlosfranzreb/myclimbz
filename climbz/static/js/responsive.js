// If the width is below 800px, show only 3 columns. Always show the first two
// columns. If the last column header says "Actions", show it. Otherwise, show#
// the third column.
function table_columns() {
    if (window.innerWidth < 800) {
        let rows = document.querySelectorAll("#content_table tr");

        let n_cols = rows[0].querySelectorAll("th").length;
        let last_header = rows[0].querySelectorAll("th")[n_cols - 1].textContent;
        let visible_idxs = [0, 1];
        if (last_header !== "Actions")
            visible_idxs.push(2);
        else
            visible_idxs.push(n_cols - 1);

        for (let row of rows) {
            for (let tag_name of ["th", "td"]) {
                let cells = row.querySelectorAll(tag_name);
                for (let i = 0; i < cells.length; i++) {
                    if (!visible_idxs.includes(i))
                        cells[i].style.display = "none";
                }
            }
        }
    }
}

// Add the event listener to the window
window.addEventListener("resize", table_columns);
window.addEventListener("load", table_columns);