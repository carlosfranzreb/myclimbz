// Display and manage the routes table

let DATA = null;
let GRADES = null;

let GRADE_SCALE = "font";  // Scale chosen with the toggle button
let ACTIVE_FILTERS = new Map();
let INCLUDE_UNSENT_CLIMBS = false;


function show_routes(data, grades) {
    DATA = data;
    GRADES = grades;

    // Parse the dates and format them to YYYY-MM-DD
    let parseTime = d3.timeParse("%a, %d %b %Y %H:%M:%S");
    let formatDate = d3.timeFormat("%Y-%m-%d");
    DATA = DATA.map(d => {
        d.dates = d.dates.map(date => formatDate(
            parseTime(date.substring(0, date.length - 4)))
        );
        return d;
    });

    plot_data();
}


// Create the table with the routes
function plot_data() {

    // Remove the previous table
    d3.select("#content_div").selectAll("*").remove();

    // Filter the data according to the active filters
    let this_data = filter_data();

    // Create the table
    let table = d3.select("#content_div").append("table")
        .attr("id", "content_table")
        .attr("class", "table table-striped");

    // Create the table head
    let thead = table.append("thead");
    let tr = thead.append("tr");
    tr.append("th").text("Name");
    tr.append("th").text("Grade");
    tr.append("th").text("Area");
    tr.append("th").text("Sector");
    tr.append("th").text("Height");
    tr.append("th").text("Inclination");
    tr.append("th").text("Landing");
    tr.append("th").text("Sent");

    // Create the table body
    let tbody = table.append("tbody");

    // Create the rows
    let rows = tbody.selectAll("tr")
        .data(this_data)
        .enter()
        .append("tr");

    // Add the cells to the rows
    rows.append("td").text(d => d.name);
    rows.append("td").text(d => GRADES.find(
        obj => obj.level === d.level)[GRADE_SCALE]
    );
    rows.append("td").text(d => d.area);
    rows.append("td").text(d => d.sector);
    rows.append("td").text(d => d.height);
    rows.append("td").text(d => d.inclination);
    rows.append("td").text(d => d.landing);
    rows.append("td").text(d => d.sent);

    // Initialize the DataTable
    window.data_table = new DataTable("#content_table", {
        perPage: 100,
        perPageSelect: false,
        searchable: true,
        nextPrev: false,
    });
}