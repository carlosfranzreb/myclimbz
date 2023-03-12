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

// Create the variable where the data will be stored
var data = null;

// Plot the data with D3.js
window.onload = function() {
    // Plot the pyramid
    let csv_data = d3.csv("data/boulders.csv");
    csv_data.then(function(all_data) {
        // Filter sent boulders
        data = all_data.filter(d => d.Sent == "yes");
        // Add the "None" option to the group menu
        document.getElementById("group-select").options.add(new Option("None", "None"));
        // Fill the markdown menus with the options
        let ids = ["x-axis-select", "group-select"];
        for (let id of ids) {
            let obj = document.getElementById(id);
            // Iterate over the keys of the pyramid
            for (let key of Object.keys(data[0]))
                obj.options.add(new Option(key, key));
        }
        // Select the "Grade" option by default in the x-axis menu
        document.getElementById("x-axis-select").value = "Grade";

        // Plot the data with the selected options
        plot_data()
    });
}

// Plot the data (a Map object) with D3.js
function plot_data() {

    // Clear the previous plot
    svg.selectAll("*").remove();

    // Get the selected options
    x_axis = document.getElementById("x-axis-select").value;
    group = document.getElementById("group-select").value;

    // Count values per x-axis key
    let unsorted_out = d3.rollup(data, v => v.length, d => d[x_axis])
    let out = null;
    if (x_axis == "Grade")  // TODO: add empty grades in between
        out = new Map([...unsorted_out].sort(compareMapGrades));
    else
        out = new Map([...unsorted_out].sort());

    // Group values by group key
    // TODO
    
    // X axis
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

    // Add Y axis
    let y = d3.scaleLinear()
        .domain([0, d3.max(out.values())])
        .range([height, 0]);

    svg.append("g").call(d3.axisLeft(y));

    // Bars
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