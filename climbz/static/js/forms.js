function dummy() {
    // If the user selects an existing area, the rock type field is hidden
    let rockTypeContainer = document.getElementById("rock_type-container");
    let area = document.getElementById("{{ session_form.area.id }}");

    // If the user clicks on the project search checkbox, date and conditions fields are hidden
    let is_project_search = document.getElementById("{{ session_form.is_project_search.id }}");
    let dateContainer = document.getElementById("date-container");
    let conditionsContainer = document.getElementById("conditions-container");

    function toggleRockTypeContainer() {
        let areaValue = area.value;
        let areaExists = false;
        for (let existingArea of document.getElementById("existingAreas").options) {
            if (existingArea.value == areaValue) {
                areaExists = true;
                break;
            }
        }
        rockTypeContainer.style.display = areaExists ? "none" : "block";
    }

    function toggleIsProjectSearch() {
        let isProjectSearch = is_project_search.checked;
        dateContainer.style.display = isProjectSearch ? "none" : "block";
        conditionsContainer.style.display = isProjectSearch ? "none" : "block";
    }

    area.addEventListener("change", toggleRockTypeContainer);
    toggleRockTypeContainer();

    is_project_search.addEventListener("change", toggleIsProjectSearch);
    toggleIsProjectSearch();
}

// Toggle the elements according to the checkbox state
function checkboxToggle(checkbox_id, element_ids) {
    let checkbox = document.getElementById(checkbox_id);
    element_ids = element_ids.split(",");
    let elements = element_ids.map(id => document.getElementById(id).parentElement);
    for (let element of elements) {
        element.style.display = checkbox.checked ? "none" : "block";
    }
}

// Toggle the elements if the input value belongs to the datalist
function datalistToggle(input_id, datalist_id, element_ids) {
    let input = document.getElementById(input_id);
    let datalist = document.getElementById(datalist_id);
    let is_datalist_option = false;
    for (let option of datalist.options) {
        if (option.value == input.value) {
            is_datalist_option = true;
            break;
        }
    }

    element_ids = element_ids.split(",");
    let elements = element_ids.map(id => document.getElementById(id).parentElement);
    for (let element of elements) {
        element.style.display = is_datalist_option ? "none" : "block";
    }
}
