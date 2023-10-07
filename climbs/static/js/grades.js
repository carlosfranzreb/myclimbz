/* Utility functions regarding grades */


// Return false if b is larger than a, true otherwise
function compare_grades(a, b) {
    let a_level = GRADES.find(obj => obj[GRADE_SCALE] == a[0]).level;
    let b_level = GRADES.find(obj => obj[GRADE_SCALE] == b[0]).level;
    return a_level - b_level;
}


// Fill in the missing grades between the lowest and highest grade
// ! The input map is expected to be sorted
function fill_grades(sorted_map) {

    let first_key = [...sorted_map.keys()][0];
    let last_key = [...sorted_map.keys()][sorted_map.size - 1];
    let first_idx = GRADES.findIndex(obj => obj[GRADE_SCALE] == first_key);
    let last_idx = GRADES.findIndex(obj => obj[GRADE_SCALE] == last_key);
    let filled_map = new Map();

    for (let i = first_idx; i < last_idx + 1; i++) {
        let grade = GRADES[i][GRADE_SCALE];
        if (!sorted_map.has(grade))
            filled_map.set(grade, 0);
        else
            filled_map.set(grade, sorted_map.get(grade));
    }

    return filled_map;
}


// Return the average level of a list of climbs
function get_avg_level(climbs) {
    let levels = climbs.map(d => GRADES.find(obj => obj[GRADE_SCALE]== d[GRADE_SCALE]).level);
    let avg_level = levels.reduce((a, b) => a + b) / levels.length;
    return avg_level;
}


// Return a map of levels to grades of the given type (font or hueco)
function grade_axis() {
    let axis_labels = new Map();
    for (let idx in GRADES)
        axis_labels.set(GRADES[idx].level, GRADES[idx][GRADE_SCALE]);    

    return axis_labels;
}

// Write both grade scales to the data
function write_both_grade_scales(data, grade_scale) {

    for (let idx in data) {
        let climb = data[idx];
        if (! ("Grade" in climb))
            continue;
        climb[grade_scale] = climb.Grade;
        let grade_idx = GRADES.findIndex(obj => obj[grade_scale] == climb.Grade);
        let other_scale = grade_scale == "font" ? "hueco" : "font";
        climb[other_scale] = GRADES[grade_idx][other_scale];
    }

    return data;
}
