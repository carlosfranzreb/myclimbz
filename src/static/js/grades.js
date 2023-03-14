/* Utility functions regarding grades */


// Return false if b is larger than a, true otherwise
function compareMapGrades(a, b) {
    a = a[0];
    b = b[0];
    // If both numbers are the same, go to letter
    if (a[0] == b[0]) { 
        // If one of the grades doesn't have a letter
        if (a.length == 1 || b.length == 1)
            return a.length >= b.length ? 1 : -1;
        // If both grades have the same letter, check for "+"
        if (a[1] == b[1])
            return a.length >= b.length ? 1 : -1;
        // If both grades have different letters, compare them
        else
            return a[1] > b[1] ? 1 : -1;
    }
    // If both numbers are different, compare them
    else
        return a[0] > b[0] ? 1 : -1;
}


// Return the next grade
function get_next_grade(grade) {
    // If the grade is a number, return it with a "+"
    if (grade.length == 1)
        return grade + "+";
    // If the grade is a number and a "+"
    else if (grade.length == 2 && grade[1] == "+") {
        // If the grade is 5+, return 6A
        if (grade == "5+")
            return "6A";
        // Otherwise, return the next number
        else
            return (parseInt(grade[0]) + 1).toString();
    }
    // If the grade contains a letter
    else {
        // If the grade ends with a "+"
        if (grade.length == 3) {
            // If the grade ends with "C+", return the next number
            if (grade.substring(grade.length - 2) == "C+")
                return (parseInt(grade[0]) + 1).toString() + "A";
            // Otherwise, return the next letter
            else
                return grade[0] + String.fromCharCode(grade.charCodeAt(1) + 1);
        }
        // If the grade does not end with a "+"
        else
            return grade + "+";
    }
}


// Fill in the missing grades between the lowest and highest grade
// ! The input map is expected to be sorted
function fill_grades(sorted_map) {
    // Create the new map, add the lowest grade and remove it from the input map
    let last_added_grade = [...sorted_map.keys()][0];
    filled_map = new Map();
    filled_map.set(last_added_grade, sorted_map.get(last_added_grade));
    sorted_map.delete(last_added_grade);
    // Iterate over the map
    for (let grade of sorted_map.keys()) {
        // Get the next grade of the last one in the output map
        let next_grade = get_next_grade(last_added_grade);
        // Add missing grades if needed
        while (next_grade != grade) {
            filled_map.set(next_grade, 0);
            next_grade = get_next_grade(next_grade);
        }
        filled_map.set(grade, sorted_map.get(grade));
        last_added_grade = grade;
    }
    return filled_map;
}