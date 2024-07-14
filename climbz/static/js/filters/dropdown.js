/* Constructs a dropdown menu widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} placeholder - The placeholder text of the dropdown menu
 * @param {string} data_column - The column of the table that the widget will filter
 */
var DropdownMenu = function (id, placeholder, data_column) {
    var self = this;
    self.left = 0;
    self.id = id;
    self.data_column = data_column;

    self.options = [];
    for (let climb of DATA) {
        let value = climb[data_column];
        //if value is an array, add each element to options
        if (value instanceof Array) {
            for (v of value) {
                if (!self.options.includes(v) && v !== null) {
                    self.options.push(v);
                }
            }
        } else if (!self.options.includes(value) && value !== null) {
            self.options.push(value);
        }
    }
    self.options.unshift("Select all");
    let selected_options = [];

    self.placeholder = placeholder;
    let wrapper = document.getElementById(id);
    wrapper.style.left = self.left + "px";
    wrapper.classList.add("btn-wrapper");
    let inner_html =
        `<button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>${self.placeholder}</button>` +
        `<div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>`;

    for (let i = 0; i < self.options.length; i++) {
        inner_html += `<button class='dropdown-item' id=${id}_${i}>${self.options[i]}</button>`;
    }
    inner_html += "</div>";
    wrapper.innerHTML = inner_html;
    self.menu = document.getElementById(`${id}_menu`);
    self.menu.style.display = "block";
    self.menu.style.display = "none";
    self.button = document.getElementById(`${id}_button`);
    function openFilters() {
        self.menu.style.display =
            self.menu.style.display === "block" ? "none" : "block";
    }
    self.button.addEventListener("click", openFilters);

    self.width = getTextWidth(self.placeholder, self.button) + 30;
    self.button.style.width = self.width + "px";
    wrapper.style.width = self.width + "px";

    let num_selected = 0;
    let num_options = self.options.length;

    // add event listeners to each option
    for (let i = 0; i < num_options; i++) {
        let option = document.getElementById(`${id}_${i}`);

        option.addEventListener("click", function () {
            if (self.options[i] === "Select all") {
                //change "Select all" to "Deselect all" and vice versa
                option.textContent =
                    option.textContent === "Select all" ? "Deselect all" : "Select all";
                let all_selected = false;
                if (option.textContent === "Deselect all") {
                    all_selected = true;
                }
                selected_options = [];
                for (let j = 1; j < num_options; j++) {
                    let option = document.getElementById(`${id}_${j}`);
                    // If "Deselect all" is clicked, add a checkmark to all options
                    if (all_selected) {
                        option.classList.add("active");
                    } else {
                        option.classList.remove("active");
                    }
                }
                if (all_selected) {
                    num_selected = num_options - 1;
                } else {
                    num_selected = 0;
                }
                self.button.style.backgroundColor = "var(--color-gray)"; //always gray since all selected == no selected
            } else {
                option.classList.toggle("active");
                if (option.classList.contains("active")) {
                    num_selected++;
                    selected_options.push(self.options[i]);
                } else {
                    num_selected--;
                    let index = selected_options.indexOf(self.options[i]);
                    selected_options.splice(index, 1);
                }
                if (num_selected === num_options - 1) {
                    document.getElementById(`${id}_0`).textContent = "Deselect all";
                    self.button.style.backgroundColor = "var(--color-gray)";
                } else {
                    if (num_selected === 0) {
                        self.button.style.backgroundColor = "var(--color-gray)";
                    } else {
                        self.button.style.backgroundColor = "var(--color-green)";
                    }
                    document.getElementById(`${id}_0`).textContent = "Select all";
                }
            }
        });
    }

    //add event listener so that dropdown menu closes when element loses focus
    document.addEventListener("click", function (event) {
        if (!wrapper.contains(event.target)) {
            self.menu.style.display = "none";
        }
    });

    //reset menu to have no items selected
    self.reset = function () {
        for (let i = 0; i < options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);
            option.classList.remove("active");
        }
        document.getElementById(`${id}_0`).textContent = "Select all";
        num_selected = 0;
        selected_options = [];
        self.button.style.backgroundColor = "var(--color-gray)";
    };

    self.filter_value = function (value) {
        if (
            (num_selected === num_options - 1 && value !== null) ||
            num_selected === 0
        ) {
            return true;
        }
        if (value instanceof Array) {
            for (v of value) {
                //if the option with value v is active, return true
                if (num_selected === 0 || selected_options.includes(v)) {
                    return true;
                }
            }
            return false;
        }
        return selected_options.includes(value);
    };
};