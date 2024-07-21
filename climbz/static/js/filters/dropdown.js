/* Constructs a dropdown menu widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} placeholder - The placeholder text of the dropdown menu
 * @param {string} data_column - The column of the table that the widget will filter
 */
class DropdownMenu {

    constructor(id, placeholder, data_column) {
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
        self.selected_options = [];

        self.placeholder = placeholder;
        let wrapper = document.getElementById(id);
        let inner_html = `
            <button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>
                ${self.placeholder}
            </button>
            <div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>
        `;
        for (let i = 0; i < this.options.length; i++) {
            inner_html += `<button class='dropdown-item' id=${id}_${i}>${this.options[i]}</button>`;
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

        // add event listeners to each option
        for (let i = 0; i < this.options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);

            option.addEventListener("click", function () {
                // toggle its active class and add/remove it from selected_options
                option.classList.toggle("active");
                if (option.classList.contains("active")) {
                    self.selected_options.push(this.options[i]);
                } else {
                    let index = self.selected_options.indexOf(this.options[i]);
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

    //reset menu to have no items selected
    reset() {
        for (let i = 0; i < this.options.length; i++) {
            let option = document.getElementById(`${this.id}_${i}`);
            option.classList.remove("active");
        }
        self.selected_options = [];
        self.button.style.backgroundColor = "var(--color-gray)";
    };

    filter_value(value) {
        if (value !== null || self.selected_options.length === 0)
            return true;

        if (value instanceof Array) {
            // if the option with value v is active, return true
            for (v of value) {
                if (self.selected_options.length === 0 || self.selected_options.includes(v))
                    return true;
            }
            return false;
        }
        return self.selected_options.includes(value);
    };
};