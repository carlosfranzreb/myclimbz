/* Utility functions regarding grades */


// Return false if b is larger than a, true otherwise
function compare_grades(a, b) {
    let a_level = GRADES.find(obj => obj.font == a[0]).level;
    let b_level = GRADES.find(obj => obj.font == b[0]).level;
    return a_level - b_level;
}


// Fill in the missing grades between the lowest and highest grade
// ! The input map is expected to be sorted
function fill_grades(sorted_map, grade_type="font") {

    let first_key = [...sorted_map.keys()][0];
    let last_key = [...sorted_map.keys()][sorted_map.size - 1];
    let first_idx = GRADES.findIndex(obj => obj[grade_type] == first_key);
    let last_idx = GRADES.findIndex(obj => obj[grade_type] == last_key);
    let filled_map = new Map();

    for (let i = first_idx; i < last_idx + 1; i++) {
        let grade = GRADES[i][grade_type];
        if (!sorted_map.has(grade))
            filled_map.set(grade, 0);
        else
            filled_map.set(grade, sorted_map.get(grade));
    }

    return filled_map;
}


// Return the average level of a list of climbs
function get_avg_level(climbs, grade_type) {
    let levels = climbs.map(d => GRADES.find(obj => obj[grade_type]== d.Grade).level);
    let avg_level = levels.reduce((a, b) => a + b) / levels.length;
    return avg_level;
}


// Return a map of levels to grades of the given type (font or hueco)
function grade_axis(grade_type) {
    let axis_labels = new Map();
    for (let idx in GRADES)
        axis_labels.set(GRADES[idx].level, GRADES[idx][grade_type]);    

    return axis_labels;
}