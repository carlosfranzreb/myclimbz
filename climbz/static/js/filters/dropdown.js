/* Constructs a dropdown menu widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} placeholder - The placeholder text of the dropdown menu
 * @param {string} data_column - The column of the table that the widget will filter
 */
class DropdownMenu {

    constructor(id, placeholder, data_column) {
        var self = this;
        this.id = id;
        this.data_column = data_column;

        this.options = [];
        for (let climb of DATA) {
            let value = climb[data_column];
            // if value is an array, add each element to options
            if (value instanceof Array) {
                for (let v of value) {
                    if (!this.options.includes(v) && v !== null)
                        this.options.push(v);
                }
            } else if (!this.options.includes(value) && value !== null)
                this.options.push(value);
        }

        this.placeholder = placeholder;
        let wrapper = document.getElementById(id);
        let inner_html = `
            <button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>
                ${this.placeholder}
            </button>
            <div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>
        `;
        for (let i = 0; i < this.options.length; i++) {
            inner_html += `<button class='dropdown-item' id=${id}_${i}>${this.options[i]}</button>`;
        }
        inner_html += "</div>";

        wrapper.innerHTML = inner_html;
        this.menu = document.getElementById(`${id}_menu`);
        this.menu.style.display = "none";
        this.button = document.getElementById(`${id}_button`);
        this.button.addEventListener("click", function () {
            self.menu.style.display =
                self.menu.style.display === "block" ? "none" : "block";
        });

        // add event listeners to each option
        this.selected_options = [];
        for (let i = 0; i < this.options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);

            // toggle its active class and add/remove it from selected_options
            option.addEventListener("click", function () {
                option.classList.toggle("active");
                if (option.classList.contains("active")) {
                    self.selected_options.push(self.options[i]);
                } else {
                    let index = self.selected_options.indexOf(self.options[i]);
                    self.selected_options.splice(index, 1);
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

    // reset menu to have no items selected
    reset() {
        for (let i = 0; i < this.options.length; i++) {
            let option = document.getElementById(`${this.id}_${i}`);
            option.classList.remove("active");
        }
        this.selected_options = [];
        this.button.style.backgroundColor = "var(--color-gray)";
    };

    // Return whether the value should be kept in the dataset
    filter_value(value) {
        if (this.selected_options.length === 0)
            return true;
        else if (value === null)
            return false;
        else if (value instanceof Array) {
            // if the option with value v is active, return true
            for (let v of value) {
                if (this.selected_options.length === 0 || this.selected_options.includes(v))
                    return true;
            }
            return false;
        }
        return this.selected_options.includes(value);
    };
};