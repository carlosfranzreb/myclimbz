/* Constructs a checkbox widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} title - The title of the widget
 * @param {string} data_column - The column of the table that the widget will filter
 * @param false_value - The value that should be filtered out when the checkbox is checked
 */
var Checkbox = function (id, title, data_column, false_value) {
    var self = this;
    self.left = 0;
    self.id = id;
    self.data_column = data_column;
    wrapper = document.getElementById(id);
    wrapper.style.left = self.left + "px";
    let inner_html = `
    <input class='form-check-input' type='checkbox' id='${id}_button'>
    <label class='form-check-label' for='${id}_button'>${title}</label>`;
    wrapper.innerHTML = inner_html;
    let button = document.getElementById(`${id}_button`);
    self.button = button;
    let label = document.querySelector(`label[for='${id}_button']`);
    self.width = getTextWidth(title, label) + 30;
    wrapper.style.width = self.width + "px";
    self.reset = function () {
        self.button.checked = false;
    };

    self.filter_value = function (value) {
        if (value === false_value) {
            return !self.button.checked;
        } else {
            return true;
        }
    };
};