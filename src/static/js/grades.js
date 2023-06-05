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


// Return the average grade of a list of climbs
function get_avg_grade(climbs) {
    let grades = climbs.map(d => d.Grade);
    grades = grades.map(d => get_grade_number(d));
    let avg_grade = grades.reduce((a, b) => a + b) / grades.length;
    return get_grade_string(avg_grade);
}