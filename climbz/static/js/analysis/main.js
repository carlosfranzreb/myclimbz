// Used for testing the plot
let PLOTTED_DATA = null;

// set the dimensions and margins of the graph
let MARGIN = { top: 30, right: 30, bottom: 70, left: 60 };
let WIDTH = 460 - MARGIN.left - MARGIN.right;
let HEIGHT = 400 - MARGIN.top - MARGIN.bottom;

// Define the options for the x-axis
let x_axis_options = {
    "level": "Grade",
    "level_consensus": "Grade - Consensus",
    "area": "Area",
    "sector": "Sector",
    "conditions": "Conditions",
    "dates": "Date: day",
    "dates_month": "Date: month",
    "dates_year": "Date: year",
    "height": "Height",
    "inclination": "Inclination",
    "landing": "Landing",
    "rating": "Rating",
    "sit_start": "Sit start",
    "sent": "Sent",
    "cruxes": "Crux",
    "n_sessions": "No. of sessions",
    "n_attempts_send": "No. of attempts",
}

/**
 * The show_plot function performs the following steps:
 * 
 * 1. Clear the previous plot by removing all elements from the svg.
 * 2. Get the selected x- and y-axis from the corresponding dropdown menus.
 * 3. If the y-axis is "Success rate", check the "include-unsent-climbs" checkbox.
 * 4. Filter the data based on whether unsent climbs should be included or not.
 * 5. Filter the data based on the active filters.
 * 6. If the filtered data is empty, return without plotting.
 * 7. Group the data by the selected x-axis key. If the key is "cruxes", "dates" or
 *   "conditions", count the number of values per unique key.
 * 8. Compute the data to be plotted based on the selected y-axis option.
 * 9. If the map contains lists of numbers as keys, replace them with their averages.
 * 10. Sort the data based on the x-axis key.
 * 11. Plot the data with D3.js.
 * 12. Store the plotted data in the DISPLAYED_DATA global variable.
 */
function show_plot() {

    // Delete the old plot
    d3.select("#content_div").select("svg").remove();

    // append the svg object to the body of the page
    let svg = d3.select("#content_div")
        .append("svg")
        .attr("width", WIDTH + MARGIN.left + MARGIN.right)
        .attr("height", HEIGHT + MARGIN.top + MARGIN.bottom)
        .append("g")
        .attr("transform",
            "translate(" + MARGIN.left + "," + MARGIN.top + ")");

    // Get the selected options
    let x_axis = document.getElementById("x-axis-select").value;
    let y_axis = document.getElementById("y-axis-select").value;

    // If the data is empty, return without plotting
    let this_data = JSON.parse(JSON.stringify(DISPLAYED_DATA));
    if (this_data.length == 0)
        return;

    // Group the data by the selected x-axis key.
    // Cruxes, dates and conditions are split into unique keys.
    // Dates are grouped by month.
    let unsorted_out = null;
    if (x_axis == "cruxes" || x_axis.includes("dates") || x_axis == "conditions") {
        if (x_axis == "dates_month") {
            this_data = this_data.map(d => {
                d.dates = d.dates.map(date => date.substring(3, 10));
                return d;
            });
            x_axis = "dates";
        } else if (x_axis == "dates_year") {
            this_data = this_data.map(d => {
                d.dates = d.dates.map(date => date.substring(6, 10));
                return d;
            });
            x_axis = "dates";
        }
        groups = d3.group(this_data, d => d[x_axis]);
        unsorted_out = new Map();
        for (let [key, value] of groups.entries()) {
            if (key == null)
                continue;
            for (let crux of key) {
                if (unsorted_out.has(crux))
                    unsorted_out.set(crux, unsorted_out.get(crux).concat(value));
                else
                    unsorted_out.set(crux, value);
            }
        }
    }
    else
        unsorted_out = d3.group(this_data, d => d[x_axis]);

    // Remove the null key if it exists
    if (unsorted_out.has(null))
        unsorted_out.delete(null);

    // Compute the data to be plotted according to the selected y-axis option
    unsorted_out = y_axis_options[y_axis]["data"](unsorted_out);

    // Sort the data
    let out = null;
    if (x_axis.includes("level")) {
        out = new Map(Array.from(unsorted_out).sort((a, b) => a[0] - b[0]));
        out = fill_grades(out);
    }
    else if (isNumeric(Array.from(unsorted_out.keys())[0])) {
        out = new Map(
            // Sort the map by the keys
            Array.from(unsorted_out).sort(
                (a, b) => parseFloat(a[0]) - parseFloat(b[0])
            )
        );
        // Fill in the missing keys
        let keys = Array.from(out.keys());
        let step = keys[1] - keys[0];
        let first_key = keys[0];
        let last_key = keys[keys.length - 1];
        let new_out = new Map();
        for (let key = first_key; key <= last_key; key += step) {
            if (out.has(key))
                new_out.set(key, out.get(key));
            else
                new_out.set(key, 0);
        }
        out = new_out;
    } else
        out = new Map(Array.from(unsorted_out).sort());

    let x = d3.scaleBand()
        .range([0, WIDTH])
        .domain(out.keys())
        .padding(0.2);

    svg.append("g")
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
            .tickFormat(function (d) { return y_labels.get(d); })
        svg.append("g").call(y_axis_obj)
    }
    else
        svg.append("g").call(d3.axisLeft(y));

    svg.selectAll("mybar")
        .data(out)
        .enter()
        .append("rect")
        .attr("x", function (d) { return x(d[0]) })
        .attr("y", function (d) { return y(d[1]) })
        .attr("width", x.bandwidth())
        .attr("height", function (d) { return HEIGHT - y(d[1]) })
        .attr("fill", "#69b3a2");

    PLOTTED_DATA = out;
}


function isNumeric(s) {
    return !isNaN(s - parseFloat(s));
}