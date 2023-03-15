// Functions related to filtering the data


// Add a filter to the list of filters
function add_filter() {
    let filterList = document.getElementById("filterList");
    let filterContainer = document.createElement("div");
    filterContainer.classList.add("filter-container");

    let filterDropdown1 = document.createElement("select");
    let filterDropdown2 = document.createElement("select");

    // add options to dropdowns
    // TODO

    // add dropdowns to container
    filterContainer.appendChild(filterDropdown1);
    filterContainer.appendChild(filterDropdown2);

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
