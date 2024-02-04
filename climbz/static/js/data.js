// Logic and variables that are common to both tables and plots

// Global variables shared by tables and plots
let DATA = null;
let GRADES = null;
let DISPLAYED_DATA = null;
let DISPLAY_FORM = "table";  // Table or plot

let GRADE_SCALE = "font";  // Scale chosen with the toggle button
let ACTIVE_FILTERS = new Map();
let INCLUDE_UNSENT_CLIMBS = false;


// Add an event listener to the checkbox "display-form-toggle"
let display_form_toggle = document.getElementById("display-form-toggle");
display_form_toggle.addEventListener("change", function () {
    DISPLAY_FORM = display_form_toggle.checked ? "plot" : "table";
    display_data();
});

function start_display(data, grades, session_date) {
    DATA = data;
    GRADES = grades;

    // Parse the dates and format them to YYYY-MM-DD
    let parseTime = d3.timeParse("%a, %d %b %Y %H:%M:%S");
    let formatDate = d3.timeFormat("%Y-%m-%d");
    DATA = DATA.map(d => {
        let parsed_dates = d.dates.map(date => parseTime(date.substring(0, date.length - 4)))
        d.dates = parsed_dates.map(date => formatDate(date));
        let max_date = Math.max(...parsed_dates);
        d.last_climbed = formatDate(max_date);
        return d;
    });

    // If session date is given, filter the data on the session date
    if (session_date != null) {
        add_filter();

        // Create the filter and change it to "Date"
        let filter_list = document.getElementById("filterList");
        let filter = filter_list.children[0];
        let select = filter.getElementsByTagName("select")[0];
        select.value = "Date";
        let event = new Event("change");
        select.dispatchEvent(event);

        // Set the start date
        let start_date = filter.getElementsByClassName("start-range")[0];
        start_date.value = session_date;
        start_date.addEventListener("change", filter_data_by_range);
        start_date.dispatchEvent(event);
    }

    display_data();
}


function display_data() {

    // Filter the data according to the active filters
    DISPLAYED_DATA = filter_data();

    // Remove the previous table or plot
    d3.select("#content_div").selectAll("*").remove();

    // hide/show plot-axes
    let plot_axes = document.getElementById("plot-axes");
    plot_axes.style.display = DISPLAY_FORM == "plot" ? "block" : "none";

    // Display the data
    if (DISPLAY_FORM == "table")
        show_table();
    else
        show_plot();
}