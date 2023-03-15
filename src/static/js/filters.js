// Functions related to filtering the data

// List of available filters
filter_options = [
    "Grade",
    "Area",
    "Inclination",
    "Landing",
    "Date",
    "Tries",
    "Sit start",
    "Height",
    "Style",
]


// Add a filter to the list of filters
function add_filter() {
    let filterList = document.getElementById("filterList");
    let filterContainer = document.createElement("div");
    filterContainer.classList.add("filter-container");

    // add dropdown menu to select filter
    let filter_selection = document.createElement("select");
    for (let option of filter_options)
        filter_selection.options.add(new Option(option, option));
    filterContainer.appendChild(filter_selection);

    // add dropdown menu to select filter value
    let filter_values = document.createElement("select");
    // TODO: fill with values
    filterContainer.appendChild(filter_values);

    // add remove button to container
    var removeButton = document.createElement("button");
    removeButton.innerText = "Remove";
    removeButton.onclick = function() {
        filterList.removeChild(filterContainer);
    };
    filterContainer.appendChild(removeButton);

    // add container to list
    filterList.appendChild(filterContainer);
}
