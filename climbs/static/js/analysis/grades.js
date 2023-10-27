/* Utility functions regarding grades */


// Fill in the missing grades between the lowest and highest levels, and replace
// the levels with the current grade scale
// ! The input map is expected to be sorted and contain levels as keys
function fill_grades(sorted_map) {

    let first_idx = [...sorted_map.keys()][0];
    let last_idx = [...sorted_map.keys()][sorted_map.size - 1];
    let filled_map = new Map();

    for (let level = first_idx; level < last_idx + 1; level++) {
        let grade = GRADES[level][GRADE_SCALE];
        if (filled_map.has(grade))
            continue;
        if (!sorted_map.has(level))
            filled_map.set(grade, 0);
        else
            filled_map.set(grade, sorted_map.get(level));
    }

    return filled_map;
}


// Return the average level of a list of climbs
function get_avg_level(climbs) {
    let levels = climbs.map(d => d.level);
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