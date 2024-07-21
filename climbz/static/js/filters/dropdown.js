/* Constructs a dropdown menu widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} placeholder - The placeholder text of the dropdown menu
 * @param {string} data_column - The column of the table that the widget will filter
 */
class DropdownMenu {

    constructor(id, placeholder, data_column) {
        var self = this;
        self.left = 0;
        self.id = id;
        self.data_column = data_column;

        self.options = [];
        for (let climb of DATA) {
            let value = climb[data_column];
            // if value is an array, add each element to options
            if (value instanceof Array) {
                for (let v of value) {
                    if (!self.options.includes(v) && v !== null)
                        self.options.push(v);
                }
            } else if (!self.options.includes(value) && value !== null)
                self.options.push(value);
        }
        this.selected_options = [];

        self.placeholder = placeholder;
        let wrapper = document.getElementById(id);
        wrapper.style.left = self.left + "px";
        wrapper.classList.add("m-2");
        let inner_html = `
            <button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>
                ${self.placeholder}
            </button>
            <div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>
        `;
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

        // add event listeners to each option
        for (let i = 0; i < self.options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);

            option.addEventListener("click", function () {
                // toggle its active class and add/remove it from selected_options
                option.classList.toggle("active");
                if (option.classList.contains("active")) {
                    this.selected_options.push(self.options[i]);
                } else {
                    let index = this.selected_options.indexOf(self.options[i]);
                    this.selected_options.splice(index, 1);
                }
            });
        }

        // add event listener so that dropdown menu closes when element loses focus
        document.addEventListener("click", function (event) {
            if (!wrapper.contains(event.target)) {
                self.menu.style.display = "none";
            }
        });
    };

    //reset menu to have no items selected
    reset() {
        for (let i = 0; i < options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);
            option.classList.remove("active");
        }
        this.selected_options = [];
        self.button.style.backgroundColor = "var(--color-gray)";
    };

    filter_value(value) {
        if (
            (this.selected_options.length === num_options - 1 && value !== null) ||
            this.selected_options.length === 0
        ) {
            return true;
        }
        if (value instanceof Array) {
            // if the option with value v is active, return true
            for (v of value) {
                if (this.selected_options.length === 0 || this.selected_options.includes(v))
                    return true;
            }
            return false;
        }
        return this.selected_options.includes(value);
    };
};