// Defines the y-axis options for the plot and defines the functions that compute
// the data to be plotted according to the selected option.

let y_axis_options = {
    "# of climbs": {
        "data": count_climbs,
        "axis_labels": null,
    },
    "# of tries": {
        "data": count_tries,
        "axis_labels": null,
    },
    "Tries per climb": {
        "data": tries_per_climb,
        "axis_labels": null,
    },
    "Success rate": {
        "data": success_rate,
        "axis_labels": null,
    },
    "Avg. grade": {
        "data": avg_grade,
        "axis_labels": grade_axis,
    },
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


// Compute the success rate per x-axis key: # sent climbs / # climbs
function success_rate(data) {
    return data;  // TODO: requires unsent boulders
}


// Compute the average grade per x-axis key
function avg_grade(data) {
    out = new Map();
    for (let [key, value] of data) {
        out.set(key, get_avg_level(value));
    }
    return out;
}
