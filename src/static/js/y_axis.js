// Defines the y-axis options for the plot and defines the functions that compute
// the data to be plotted according to the selected option.

let y_axis_options = {
    "# of climbs": count_climbs,
    "# of tries": count_tries,
    "Tries per climb": tries_per_climb,
    "Success rate": success_rate,
    "Avg. grade": avg_grade,
}


// Count the number of climbs per x-axis key
function count_climbs(data) {
    out = new Map();
    for (let [key, value] of data)
        out.set(key, value.length);
    return out;
}


// Count the number of tries per x-axis key
function count_tries(data) {
    out = new Map();
    for (let [key, value] of data) {
        let tries = value.map(d => d.Tries);
        tries = tries.reduce((a, b) => parseInt(a) + parseInt(b));
        out.set(key, tries);
    }
    return out;
}


// Compute the tries per climb per x-axis key
function tries_per_climb(data) {
    out = new Map();
    for (let [key, value] of data) {
        let tries = value.map(d => d.Tries);
        tries = tries.reduce((a, b) => parseInt(a) + parseInt(b));
        out.set(key, tries / value.length);
    }
    return out;
}


// Compute the success rate per x-axis key: # of climbs / # of sent climbs
function success_rate(data) {  // TODO: copilot predicted this function
    return data;  // TODO
}

// Compute the average grade per x-axis key
function avg_grade(data) {
    return data; // TODO
}