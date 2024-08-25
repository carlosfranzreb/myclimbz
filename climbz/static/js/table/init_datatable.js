function init_datatable() {

    // Check if the DataTable already exists
    if (window.data_table !== undefined)
        return;

    // Initialize the DataTable
    window.data_table = new simpleDatatables.DataTable("#content_table", {
        perPage: 100,
        perPageSelect: false,
        searchable: true,
        nextPrev: false,
    });

    // Sort the DataTable
    let table_element = document.getElementById("content_table");
    let sort_column_idx = table_element.getAttribute("data-sort-col");
    let sort_order = table_element.getAttribute("data-sort-order");
    window.data_table.columns.sort(sort_column_idx, sort_order);
}

window.addEventListener("load", function () {
    init_datatable();
});