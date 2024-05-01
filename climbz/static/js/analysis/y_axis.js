// Defines the y-axis options for the plot and defines the functions that compute
// the data to be plotted according to the selected option.

let y_axis_options = {
    "Attempts: total": {
        "data": count_attempts,
        "axis_labels": null,
    },
    "Attempts: avg.": {
        "data": avg_attempts_per_climb,
        "axis_labels": null,
    },
    "Attempts: min.": {
        "data": min_attempts_per_climb,
        "axis_labels": null,
    },
    "Attempts: max.": {
        "data": max_attempts_per_climb,
        "axis_labels": null,
    },
    "Climbs: total tried": {
        "data": count_climbs,
        "axis_labels": null,
    },
    "Climbs: total sent": {
        "data": count_climbs_sent,
        "axis_labels": null,
    },
    "Climbs: success rate": {
        "data": success_rate,
        "axis_labels": null,
    },
    "Grade: avg.": {
        "data": avg_grade,
        "axis_labels": grade_axis,
    },
    "Grade: max.": {
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

// Count the number of climbs sent per x-axis key
function count_climbs_sent(data) {
    out = new Map();
    for (let [key, value] of data) {
        out.set(key, 0);
        for (let climb of value) {
            if (climb.sent === true)
                out.set(key, out.get(key) + 1);
        }
    }
    return out;
}


// Count the number of attempts per x-axis key
function count_attempts(data) {
    out = new Map();
    for (let [key, value] of data) {
        let attempts = value.map(d => d.n_attempts_send);
        attempts = attempts.reduce((a, b) => parseInt(a) + parseInt(b));
        out.set(key, attempts);
    }
    return out;
}


// Compute the attempts per climb per x-axis key
function avg_attempts_per_climb(data) {
    climbs_count = count_climbs(data);
    attempts_count = count_attempts(data);
    out = new Map();
    for (let [key, value] of data)
        out.set(key, attempts_count.get(key) / climbs_count.get(key));
    return out;
}

// Compute the min attempts per climb per x-axis key
function min_attempts_per_climb(data) {
    out = new Map();
    for (let [key, value] of data) {
        let attempts = value.map(d => d.n_attempts_send);
        out.set(key, Math.min(...attempts));
    }
    return out;
}


// Compute the max attempts per climb per x-axis key
function max_attempts_per_climb(data) {
    out = new Map();
    for (let [key, value] of data) {
        let attempts = value.map(d => d.n_attempts_send);
        out.set(key, Math.max(...attempts));
    }
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