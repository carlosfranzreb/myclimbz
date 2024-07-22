/* Constructs a radio button widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} data_column - The column of the table that the widget will filter
 * @param {Array} options - The options that the radio buttons will display
 * @param {Array} truth_values - The values that when the corresponding radio button is selected, will be filtered in
 */
class RadioButton {

    constructor(id, data_column, options, truth_values) {
        this.id = id;
        this.data_column = data_column;
        this.truth_values = truth_values;

        let wrapper = document.getElementById(id);
        wrapper.innerHTML = "";

        for (let i in options) {
            let form_elem = document.createElement("div");
            form_elem.className = "form-check";
            form_elem.id = `${id}_form_${i}`;
            wrapper.appendChild(form_elem);
            let elem = document.createElement("input");
            elem.className = "form-check-input";
            elem.type = "radio";
            elem.id = `${id}_${i}`;
            elem.name = id;
            if (i === "0") {
                elem.checked = true;
            }
            form_elem.appendChild(elem);
            let label = document.createElement("label");
            label.className = "form-check-label";
            label.htmlFor = `${id}_${i}`;
            label.innerHTML = options[i];
            form_elem.appendChild(label);
        }
    };

    reset() {
        document.getElementById(`${this.id}_0`).checked = true;
    };

    filter_value(value) {
        let checked = document.querySelector(`input[name=${this.id}]:checked`);
        let index = checked.id.split("_").pop();
        let t = this.truth_values[index];
        if (t instanceof Array) {
            return t.includes(value);
        }
        return value === t;
    };
};