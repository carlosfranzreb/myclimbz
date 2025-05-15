/**
 * This script handles the "Climbing sections" form, adding and removing
 * sections as needed.
 */

let currentFrameIndex = 0;

const addSectionBtn = document.getElementById("add-section-btn");
const sectionsContainer = document.getElementById("sections-container");

// Add info text about the number of attempts that are annotated
let annotatedInfoParagraph = document.createElement("p");
annotatedInfoParagraph.id = "n_attempts-annotated-info";
annotatedInfoParagraph.className = "text-muted";
annotatedInfoParagraph.innerHTML =
	"No. of attempts annotated: <span id='n_attempts-annotated-span'>1</span>";

let nAttemptsField = document.getElementById("n_attempts");
nAttemptsField.value = 1;
nAttemptsField.parentElement.appendChild(annotatedInfoParagraph);
let annotatedAttemptsSpan = document.getElementById(
	"n_attempts-annotated-span"
);

// --- Event Listener: Add Section ---
addSectionBtn.addEventListener("click", () => {
	// Next index is the current count
	const newIndex =
		sectionsContainer.querySelectorAll(".section-entry").length;

	// Clone the first section
	const newSection = sectionsContainer
		.querySelector(".section-entry")
		.cloneNode(true);

	// Change the IDs of the input fields and their labels, and empty them
	["start", "end", "file", "sent"].forEach((field) => {
		const inputField = newSection.querySelector(`#sections-0-${field}`);
		let newId = `sections-${newIndex}-${field}`;
		inputField.id = newId;
		inputField.name = newId;
		inputField.value = "";

		// Change the label
		const label = newSection.querySelector(
			`label[for="sections-0-${field}"]`
		);
		if (label) label.setAttribute("for", `sections-${newIndex}-${field}`);
	});

	// Remove error messages, if any
	newSection.querySelectorAll(".invalid-feedback").forEach((element) => {
		element.remove();
	});

	// Add remove button
	const removeContainer = document.createElement("div");
	removeContainer.classList.add("col-md-5", "col", "text-end");
	const removeBtn = document.createElement("button");
	removeBtn.textContent = "Remove";
	removeBtn.classList.add(
		"btn",
		"btn-danger",
		"btn-sm",
		"remove-section-btn"
	);
	removeBtn.addEventListener("click", handleRemoveClick);
	removeContainer.appendChild(removeBtn);
	newSection.querySelectorAll(":scope > div")[1].appendChild(removeContainer);

	// Update the number of attempts and the info text of the climb form
	nAttemptsField.value++;
	annotatedAttemptsSpan.textContent = (
		parseInt(annotatedAttemptsSpan.textContent, 10) + 1
	).toString();

	// Append the new section to the container
	sectionsContainer.appendChild(newSection);
});

// Event Listener to remove a section; the number of attempts in the climb form is updated
function handleRemoveClick(event) {
	event.target.closest(".section-entry").remove();
	nAttemptsField.value--;
	annotatedAttemptsSpan.textContent = (
		parseInt(annotatedAttemptsSpan.textContent, 10) - 1
	).toString();
}
