// Retrieve the checkbox element
let customAxisToggle = document.getElementById("grade-scale-toggle");

// Add an event listener to the checkbox
customAxisToggle.addEventListener("change", function() {
    let is_checked = customAxisToggle.checked;
    GRADE_SCALE = is_checked ? "hueco" : "font";

    if (GRADE_SCALE != DATA_GRADE_SCALE) {
        for (let idx in DATA) {
            let current_grade = DATA[idx].Grade;
            let grade_idx = GRADES.findIndex(obj => obj[DATA_GRADE_SCALE] == current_grade);
            let new_grade = GRADES[grade_idx][GRADE_SCALE]
            DATA[idx].Grade = new_grade;
        }
        DATA_GRADE_SCALE = GRADE_SCALE;
    }

    plot_data();
});