// Create the table with the routes
function show_table() {

    // Create the table
    let table = d3.select("#content_div").append("table")
        .attr("id", "content_table")
        .attr("class", "table table-striped table-hover");

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
    tr.append("th").text("Last climbed");

    // Create the table body
    let tbody = table.append("tbody");

    // Create the rows with onclick attribute
    let rows = tbody.selectAll("tr")
        .data(DISPLAYED_DATA)
        .enter()
        .append("tr")
        .attr("onclick", function (d) {
            return "window.location = '/route/" + d.id + "';";
        });

    // Add the cells to the rows
    rows.append("td").text(d => d.name);
    rows.append("td").text(d => {
        if (d.level === null)
            return "N/A";
        else
            return GRADES.find(obj => obj.level === d.level)[GRADE_SCALE];
    });
    rows.append("td").text(d => d.area);
    rows.append("td").text(d => d.sector);
    rows.append("td").text(d => d.height);
    rows.append("td").text(d => d.inclination);
    rows.append("td").text(d => d.landing);
    rows.append("td").text(d => d.sent);
    rows.append("td").text(d => d.last_climbed);

    // Initialize the DataTable
    window.data_table = new DataTable("#content_table", {
        perPage: 100,
        perPageSelect: false,
        searchable: true,
        nextPrev: false,
    });
}