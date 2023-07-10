// Add a filter with a list of checkboxes to select options, and a button to
// select all options.
function add_filter_dates(div, column) {

    // Add the start- and end-date inputs
    for (let id of ["start", "end"]) {
        let date_input = document.createElement("input");
        date_input.setAttribute("type", "date");
        date_input.setAttribute("id", id + "-date");
        date_input.addEventListener("change", filter_data_by_dates);
        div.appendChild(date_input);
    }
}


// Get the selected dates and filter the data
function filter_data_by_dates() {

    // Get the selected dates
    let start_date = new Date(document.getElementById("start-date").value);
    let end_date = new Date(document.getElementById("end-date").value);

    // Find the dates that are within the selected range
    let selected_dates = [];
    for (let climb of DATA) {
        let date = moment(climb["Date"], "DD/MM/YYYY").toDate();
        if (isNaN(date))
            continue;
        if (! isNaN(start_date) && date < start_date)
            continue;
        if (! isNaN(end_date) && date > end_date)
            continue;
        selected_dates.push(climb["Date"]);
    }

    // Add the filter
    ACTIVE_FILTERS.set("Date", selected_dates);
    plot_data();
}