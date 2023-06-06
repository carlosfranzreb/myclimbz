// set the dimensions and margins of the graph
let margin = {top: 30, right: 30, bottom: 70, left: 60};
let width = 460 - margin.left - margin.right;
let height = 400 - margin.top - margin.bottom;

// append the svg object to the body of the page
let svg = d3.select("#chart")
    .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
    .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

// Create the variables where the data and grades will be stored
let DATA = null;
let GRADES = null;
let GRADE_SCALE = "font";  // Scale chosen with the toggle button
let DATA_GRADE_SCALE = "font";  // Scale used in the CSV file

// Plot the data with D3.js
window.onload = function() {
    
    let data_promise = d3.csv("data/boulders.csv");
    let grades_promise = d3.json("data/grades.json");

    Promise.all([data_promise, grades_promise]).then(function([data, grades]) {
        DATA = data.filter(d => d.Sent == "yes");
        GRADES = grades;

        // Add the x-axis options to the menu, as defined in y_axis.js
        for (let key of Object.keys(y_axis_options))
            document.getElementById("y-axis-select").options.add(
                new Option(key, key)
            );

        // Fill the x-axis options with the keys of the first data element
        for (let key of Object.keys(DATA[0]))
            document.getElementById("x-axis-select").options.add(new Option(key, key));

        // Select the "Grade" option by default in the x-axis menu
        document.getElementById("x-axis-select").value = "Grade";

        plot_data();
    });
}


// Plot the data (a Map object) with D3.js
function plot_data() {

    // Clear the previous plot
    svg.selectAll("*").remove();

    // Get the selected options
    x_axis = document.getElementById("x-axis-select").value;
    y_axis = document.getElementById("y-axis-select").value;

    // Group the data by the selected x-axis key
    let unsorted_out = d3.group(DATA, d => d[x_axis]);

    // Compute the data to be plotted according to the selected y-axis option
    unsorted_out = y_axis_options[y_axis]["data"](unsorted_out);

    // Sort the data
    let out = null;
    if (x_axis == "Grade") {
        out = new Map([...unsorted_out].sort(compare_grades));
        out = fill_grades(out);
    }
    else
        out = new Map([...unsorted_out].sort());
    
    console.log(out);
    console.log(DATA);
    
    let x = d3.scaleBand()
        .range([ 0, width ])
        .domain(out.keys())
        .padding(0.2);

    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)")
        .style("text-anchor", "end");

    let y = d3.scaleLinear()
        .domain([0, d3.max(out.values())])
        .range([height, 0]);

    if (y_axis_options[y_axis]["axis_labels"] != null) { 
        let y_labels = y_axis_options[y_axis]["axis_labels"]();
        console.log(y_labels);
        let y_axis_obj = d3.axisLeft(y)
            .tickFormat(function(d){ return y_labels.get(d); })
        svg.append("g").call(y_axis_obj)
    }
    else {
        svg.append("g")
            .call(d3.axisLeft(y));
    }

    svg.selectAll("mybar")
        .data(out)
        .enter()
        .append("rect")
            .attr("x", function(d) { return x(d[0]) })
            .attr("y", function(d) { return y(d[1]) })
            .attr("width", x.bandwidth())
            .attr("height", function(d) { return height - y(d[1]) })
            .attr("fill", "#69b3a2");
}
