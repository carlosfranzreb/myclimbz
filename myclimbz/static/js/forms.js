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

/**
 * Given the title of a form, reset its fields to be empty or in the case of sliders
 * to their default values. "n_attempts" is also a special case, where the content of
 * the info message is used to update it. There are several messages to inform the user
 * that data was fetched from the database to fill the form; these messages are also
 * removed here.
 */
function resetForm(formTitle) {
	// Find the H4 element with the matching title to get the form container
	let titleElement = Array.from(document.getElementsByTagName("h4")).find(
		function (el) {
			return el.textContent.trim() === formTitle;
		}
	);
	let formContainer = titleElement.parentElement;

	// Remove the 'fetched from database' messages
	let fetchedMsg = titleElement.nextElementSibling;
	if (
		fetchedMsg &&
		fetchedMsg.tagName === "P" &&
		fetchedMsg.classList.contains("text-muted") &&
		fetchedMsg.textContent.includes("fetched from the database")
	) {
		fetchedMsg.remove();
	}

	// Update the number of attempts and remove the message if needed
	let nAttemptsDbInfo = formContainer.querySelector("#n_attempts-db-info");
	if (nAttemptsDbInfo) {
		let infoText = nAttemptsDbInfo.textContent;
		let matches = infoText.match(/\d+/);
		if (matches) {
			let fetchedAttempts = parseInt(matches[0], 10);
			let nAttemptsField = formContainer.querySelector("#n_attempts");
			if (nAttemptsField)
				nAttemptsField.value =
					parseInt(nAttemptsField.value, 10) - fetchedAttempts;
		}
		nAttemptsDbInfo.remove();
	}

	// Reset form fields
	let fields = formContainer.querySelectorAll(
		"input[type=text], input[type=number], input[type=checkbox], input[type=range], select, textarea"
	);
	fields.forEach(function (field) {
		// Skip n_attempts, which was updated above
		if (field.id === "n_attempts") return;

		switch (field.type) {
			// Reset range sliders to 3 and update their output
			case "range":
				field.value = "3";
				let output = document.getElementById(field.id + "-output");
				output.value = "3";
				break;

			// Uncheck checkboxes
			case "checkbox":
				field.checked = false;
				break;

			// Clear text-based inputs, textareas and number-based inputs
			case "textarea":
			case "text":
			case "number":
				field.value = "";
				break;

			// Select first option of select field (should be an empty string)
			case "select-one":
				field.selectedIndex = 0;
				break;
		}
	});
}

/**
 * 1. Fetch the given URL and convert the response to a JSON.
 * 2. If the JSON is empty, call resetForm() with the corresponding title.
 * 3. If not, call the given function and pass it the data to fill the form.
 */
function fetchDataAndUpdateForm(url, func, formTitle) {
	fetch(url)
		.then(function (response) {
			return response.json();
		})
		.then(function (data) {
			if (!data || Object.keys(data).length === 0)
				return resetForm(formTitle);
			else return func(data);
		})
		.catch(function (error) {
			console.error("Error fetching data:", error);
		});
}

/**
 * Function to fill the opinion form given a dictionary.
 * This function is passed to fetchDataAndUpdateForm as an argument.
 */
function updateOpinionForm(data) {
	// Add a paragraph below the title warning the user that this info was fetched from the DB
	let opinionTitleElement = Array.from(
		document.getElementsByTagName("h4")
	).find(function (el) {
		return el.textContent.trim() === "Opinion";
	});
	if (opinionTitleElement) {
		opinionTitleElement.insertAdjacentHTML(
			"afterend",
			'<p class="text-muted">Existing opinion was fetched from the database.</p>'
		);
	}

	// Update grade and comment; both could be null (TODO: comment QA)
	["grade", "opinion_comment"].forEach(function (field) {
		if (data[field]) document.getElementById(field).value = data[field];
	});

	// Update rating and landing slider values and their labels
	["rating", "landing"].forEach(function (field) {
		document.getElementById(field).value = data[field];
		document.getElementById(field + "-output").value = data[field];
	});

	// Update cruxes
	var cruxesList = document.getElementById("cruxes");
	var checkboxes = cruxesList.querySelectorAll("input[type='checkbox']");
	checkboxes.forEach(function (checkbox) {
		var label = checkbox.nextElementSibling;
		var cruxName = label ? label.textContent.trim() : "";
		checkbox.checked = data.cruxes.includes(cruxName);
	});
}

/**
 * Function to fill the climb form given a dictionary.
 * This function is passed to fetchDataAndUpdateForm as an argument.
 */
function updateClimbForm(data) {
	// Add a paragraph below the title warning the user that this info was fetched from the DB
	let opinionTitleElement = Array.from(
		document.getElementsByTagName("h4")
	).find(function (el) {
		return el.textContent.trim() === "Climb";
	});
	if (opinionTitleElement) {
		opinionTitleElement.insertAdjacentHTML(
			"afterend",
			'<p class="text-muted">Existing climb was fetched from the database.</p>'
		);
	}

	// Update texts
	["climb_comment", "climb_link"].forEach(function (field) {
		if (data[field]) document.getElementById(field).value = data[field];
	});

	// Update the checkboxes for "sent" and "flashed"
	["sent", "flashed"].forEach(function (field) {
		document.getElementById(field).checked = data[field];
	});

	// Update the number of attempts
	let nAttemptsField = document.getElementById("n_attempts");
	if (nAttemptsField) {
		let currentValue = parseInt(nAttemptsField.value, 10) || 0;
		let fetchedAttempts = parseInt(data.n_attempts, 10) || 0;
		nAttemptsField.value = currentValue + fetchedAttempts;
		let infoText = "No. of attempts in database: " + fetchedAttempts;
		let dbInfoId = "n_attempts-db-info";
		let dbInfoParagraph = document.getElementById(dbInfoId);
		if (dbInfoParagraph) {
			dbInfoParagraph.textContent = infoText;
		} else {
			dbInfoParagraph = document.createElement("p");
			dbInfoParagraph.id = dbInfoId;
			dbInfoParagraph.className = "text-muted";
			dbInfoParagraph.textContent = infoText;
			nAttemptsField.parentElement.appendChild(dbInfoParagraph);
		}
	}
}
