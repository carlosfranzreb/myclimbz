// Plot the data with D3.js
window.onload = function() {
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

    // Parse the data
    let csv_data = d3.csv("data/boulders.csv");

    csv_data.then(function(data) {
        // Group no. of sent boulders per grade
        let sent = data.filter(d => d.Sent == "yes");
        let unsorted_pyramid = d3.rollup(sent, v => v.length, d => d.Grade)

        // Sort the data by grade
        let pyramid = new Map([...unsorted_pyramid].sort(compareMapGrades));

        // X axis
        let x = d3.scaleBand()
            .range([ 0, width ])
            .domain(pyramid.keys())
            .padding(0.2);

        svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "translate(-10,0)rotate(-45)")
            .style("text-anchor", "end");

        // Add Y axis
        let y = d3.scaleLinear()
            .domain([0, d3.max(pyramid.values())])
            .range([height, 0]);
        
        svg.append("g")
            .call(d3.axisLeft(y));

        // Bars
        svg.selectAll("mybar")
            .data(pyramid)
            .enter()
            .append("rect")
                .attr("x", function(d) { return x(d[0]) })
                .attr("y", function(d) { return y(d[1]) })
                .attr("width", x.bandwidth())
                .attr("height", function(d) { return height - y(d[1]) })
                .attr("fill", "#69b3a2");
    });
}