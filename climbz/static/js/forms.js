// Toggle the elements according to the checkbox state
function checkboxToggle(checkbox_id, element_ids) {
	let checkbox = document.getElementById(checkbox_id);
	element_ids = element_ids.split(",");
	let elements = element_ids.map(
		(id) => document.getElementById(id).parentElement
	);
	for (let element of elements) {
		element.style.display = checkbox.checked ? "none" : "block";
	}
}

/** 
Toggle the elements if the input value belongs to the datalist

relation_field is the optional id of the related field. The combination of this field and the
related field together determine the toggling. If the input value is in the datalist and related
value is empty, the related value will be automatically set to the appropriate value,
as defined in the relation_data dictionary. Otherwise, if the related field is not empty and
its relationship with the input value is not present in the relation_data dictionary, the
toggling will not be performed.

- relation_field is the id of the related field.
- relation_data maps options of the input datalist to options of the related fields' datalist.
	It must have a datalist.

*/
function datalistToggle(input_id, element_ids, relation_field, relation_data) {
	// Check if the input value is in the datalist
	let input = document.getElementById(input_id);
	let datalist = document.getElementById(input_id + "-list");
	let is_datalist_option = false;
	for (let option of datalist.options) {
		if (option.value == input.value) {
			is_datalist_option = true;
			break;
		}
	}

	if (is_datalist_option && relation_field !== "") {
		// Get the index of the input value in the datalist
		let input_idx = -1;
		for (let i = 0; i < datalist.options.length; i++) {
			if (datalist.options[i].value == input.value) {
				input_idx = i;
				break;
			}
		}

		// Parse the relation data and get the expected value
		let related_field = document.getElementById(relation_field);
		let related_datalist = document.getElementById(
			relation_field + "-list"
		);
		let relation_data_arr = relation_data
			.replace(/[\[\]]/g, "")
			.split(",")
			.map((x) => parseInt(x));

		let expected_value =
			related_datalist.options[relation_data_arr[input_idx]].value;

		// Check if the relation is fullfilled
		let relation_fullfilled = true;
		if (related_field.value == "") related_field.value = expected_value;
		else relation_fullfilled = related_field.value == expected_value;
		is_datalist_option = is_datalist_option && relation_fullfilled;

		// Add onchange event to the related field
		related_field.onchange = function () {
			datalistToggle(
				input_id,
				element_ids,
				relation_field,
				relation_data
			);
		};
	}

	// Toggle the elements
	let elements = element_ids
		.split(",")
		.map((id) => document.getElementById(id).parentElement);
	for (let element of elements) {
		let inputChild = element.querySelector("input");
		let visible_value =
			inputChild && inputChild.classList.contains("form-check")
				? "flex"
				: "block";
		element.style.display = is_datalist_option ? "none" : visible_value;
	}
}
