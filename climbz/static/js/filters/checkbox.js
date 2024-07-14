/* Constructs a checkbox widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} title - The title of the widget
 * @param {string} data_column - The column of the table that the widget will filter
 * @param false_value - The value that should be filtered out when the checkbox is checked
 */
class Checkbox {
    constructor(id, title, data_column, false_value) {
        this.left = 0;
        this.id = id;
        this.data_column = data_column;
        wrapper = document.getElementById(id);
        wrapper.style.left = this.left + "px";
        let inner_html = `
            <input class='form-check-input' type='checkbox' id='${id}_button'>
            <label class='form-check-label' for='${id}_button'>${title}</label>
        `;
        wrapper.innerHTML = inner_html;
        this.button = document.getElementById(`${id}_button`);
        let label = document.querySelector(`label[for='${id}_button']`);
        this.width = getTextWidth(title, label) + 30;
        wrapper.style.width = self.width + "px";
    };

    reset() {
        this.button.checked = false;
    };

    filter_value(value) {
        if (value === false_value)
            return !this.button.checked;
        else
            return true;
    };
};