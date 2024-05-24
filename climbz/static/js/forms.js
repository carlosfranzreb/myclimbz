// Fire all onchange events on page load
window.onload = function () {
    var elements = document.querySelectorAll('*');
    for (var i = 0; i < elements.length; i++) {
        if (elements[i].onchange)
            elements[i].onchange();
    }
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
