const MOBILE_WIDTH = 900;

// Initialize and sort the DataTable
function init_datatable() {
	window.data_table = new simpleDatatables.DataTable("#content_table", {
		perPage: 100,
		perPageSelect: false,
		searchable: true,
		nextPrev: false,
	});

	let table_element = document.getElementById("content_table");
	let sort_column_idx = table_element.getAttribute("data-sort-col");
	let sort_order = table_element.getAttribute("data-sort-order");
	window.data_table.columns.sort(sort_column_idx, sort_order);
	hide_columns();
}

// If the width is below 800px, show only 3 columns. Always show the first two
// columns. If the last column header says "Actions", show it. Otherwise, show
// the third column.
// Also, when the cursor is over the table, change the cursor to a pointer.
function hide_columns() {
	if (!window.data_table) return;

	window.data_table.dom.style.cursor = "pointer";
	if (window.innerWidth < MOBILE_WIDTH) {
		// load the table and check if it hiding is needed
		let n_cols = window.data_table.columns.size();
		if (n_cols <= 3) return;
		if (!window.data_table.columns.visible(n_cols - 1)) return;

		// get the last header
		let last_header =
			window.data_table.dom.querySelectorAll("thead tr th")[n_cols - 1]
				.textContent;

		// hide columns based on the last header
		let hide_indices = [...Array(n_cols).keys()].slice(2);
		if (last_header !== "Actions") hide_indices = hide_indices.slice(1);
		else hide_indices = hide_indices.slice(0, -1);
		window.data_table.columns.hide(hide_indices);
	}
}

window.addEventListener("load", init_datatable);
window.addEventListener("resize", hide_columns);
