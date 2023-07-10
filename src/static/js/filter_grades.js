// Add a filter with a list of checkboxes to select options, and a button to
// select all options.
function add_filter_grades(div, column) {

    // Add the start- and end-grade inputs
    for (let id of ["start", "end"]) {
        let grade_input = document.createElement("select");

        // Add the options
        for (let grade of GRADES) {
            let option = document.createElement("option");
            option.setAttribute("value", grade[GRADE_SCALE]);
            option.innerText = grade[GRADE_SCALE];
            grade_input.appendChild(option);
        }

        // If this is the end-grade input, select the last grade
        if (id == "end")
            grade_input.selectedIndex = grade_input.options.length - 1;

        grade_input.setAttribute("id", id + "-grade");
        grade_input.addEventListener("change", filter_data_by_grades);
        div.appendChild(grade_input);
    }
}


// Get the selected grades and filter the data
function filter_data_by_grades() {

    // Get the selected grades
    let start_grade = document.getElementById("start-grade").value;
    let end_grade = document.getElementById("end-grade").value;

    // Find the grades that are within the selected range
    let selected_grades = [];
    for (let climb of DATA) {
        let grade = climb["Grade"];
        
        if (compare_grades([grade], [start_grade]) < 0)
            continue;
        if (compare_grades([grade], [end_grade]) > 0)
            continue;
        selected_grades.push(grade);
    }

    // Add the filter
    ACTIVE_FILTERS.set("Grade", selected_grades);
    plot_data();
}