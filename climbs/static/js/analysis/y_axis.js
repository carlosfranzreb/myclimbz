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
    "Max. grade": {
        "data": max_grade,
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
        let tries = value.map(d => d.n_attempts_send);
        tries = tries.reduce((a, b) => parseInt(a) + parseInt(b));
        out.set(key, tries);
    }
    return out;
}


// Compute the tries per climb per x-axis key
function tries_per_climb(data) {
    climbs_count = count_climbs(data);
    tries_count = count_tries(data);
    out = new Map();
    for (let [key, value] of data)
        out.set(key, tries_count.get(key) / climbs_count.get(key));
    return out;
}


// Compute the success rate per x-axis key: # sent climbs / # climbs
// ! Assume that data contains unsent climbs
function success_rate(data) {

    out = new Map();
    for (let [key, value] of data) {
        let sent_climbs = value.filter(d => d.sent === true);
        if (value.length == 0)
            out.set(key, 0);
        else
            out.set(key, sent_climbs.length / value.length);
    }

    return out;    
}


// Compute the average grade per x-axis key
function avg_grade(data) {
    out = new Map();
    for (let [key, value] of data)
        out.set(key, get_avg_level(value));
    return out;
}


// Compute the max grade per x-axis key
function max_grade(data) {
    out = new Map();
    for (let [key, value] of data)
        out.set(key, get_max_level(value));
    return out;
}
