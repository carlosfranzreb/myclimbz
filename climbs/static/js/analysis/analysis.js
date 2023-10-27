// set the dimensions and margins of the graph
let MARGIN = {top: 30, right: 30, bottom: 70, left: 60};
let WIDTH = 460 - MARGIN.left - MARGIN.right;
let HEIGHT = 400 - MARGIN.top - MARGIN.bottom;


// append the svg object to the body of the page
let SVG = d3.select("#chart")
    .append("svg")
        .attr("width", WIDTH + MARGIN.left + MARGIN.right)
        .attr("height", HEIGHT + MARGIN.top + MARGIN.bottom)
    .append("g")
        .attr("transform",
            "translate(" + MARGIN.left + "," + MARGIN.top + ")");

// Create the variables where the data and grades will be stored
let DATA = null;
let GRADES = null;
let GRADE_SCALE = "font";  // Scale chosen with the toggle button
let DATA_GRADE_SCALE = "font";  // Scale used in the CSV file
let ACTIVE_FILTERS = new Map();
let INCLUDE_UNSENT_CLIMBS = false;


// Plot the data with D3.js
function start_analysis(data, grades) {
    
    DATA = data;
    GRADES = grades;

    // Add the x-axis options to the menu, as defined in y_axis.js
    for (let key of Object.keys(y_axis_options))
        document.getElementById("y-axis-select").options.add(
            new Option(key, key)
        );

    // Fill the x-axis options with the keys of the first data element
    for (let key of Object.keys(DATA[0]))
        document.getElementById("x-axis-select").options.add(new Option(key, key));
    document.getElementById("x-axis-select").value = "level";

    plot_data();
}


// Plot the data (a Map object) with D3.js
function plot_data() {

    // Clear the previous plot
    SVG.selectAll("*").remove();

    // Get the selected options
    let x_axis = document.getElementById("x-axis-select").value;
    let y_axis = document.getElementById("y-axis-select").value;
    if (y_axis == "Success rate" && ! unsent_climbs_btn.checked) {
        document.getElementById("include-unsent-climbs").checked = true;
        INCLUDE_UNSENT_CLIMBS = true;
    }

    // Remove unsent climbs if the corresponding button is unchecked
    let this_data = null;
    if (INCLUDE_UNSENT_CLIMBS)
        this_data = DATA
    else
        this_data = DATA.filter(d => d.sent === true);

    // Filter the data according to the active filters
    for (let [key, value] of ACTIVE_FILTERS)
        this_data = this_data.filter(d => value.includes(d[key]));

    // If the data is empty, return without plotting
    if (this_data.length == 0)
        return;

    // Group the data by the selected x-axis key
    let unsorted_out = d3.group(this_data, d => d[x_axis]);

    // Compute the data to be plotted according to the selected y-axis option
    unsorted_out = y_axis_options[y_axis]["data"](unsorted_out);

    // Sort the data
    let out = null;
    if (x_axis == "level") {
        out = new Map(Array.from(unsorted_out).sort((a, b) => a[0] - b[0]));
        out = fill_grades(out);
    }
    else
        out = new Map(Array.from(unsorted_out).sort());
    
    let x = d3.scaleBand()
        .range([ 0, WIDTH ])
        .domain(out.keys())
        .padding(0.2);

    SVG.append("g")
        .attr("transform", "translate(0," + HEIGHT + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");

    let y = d3.scaleLinear()
        .domain([0, d3.max(out.values())])
        .range([HEIGHT, 0]);

    if (y_axis_options[y_axis]["axis_labels"] != null) { 
        let y_labels = y_axis_options[y_axis]["axis_labels"]();
        let y_axis_obj = d3.axisLeft(y)
            .tickFormat(function(d){ return y_labels.get(d); })
        SVG.append("g").call(y_axis_obj)
    }
    else {
        SVG.append("g")
            .call(d3.axisLeft(y));
    }

    SVG.selectAll("mybar")
        .data(out)
        .enter()
        .append("rect")
            .attr("x", function(d) { return x(d[0]) })
            .attr("y", function(d) { return y(d[1]) })
            .attr("width", x.bandwidth())
            .attr("height", function(d) { return HEIGHT - y(d[1]) })
            .attr("fill", "#69b3a2");
}
