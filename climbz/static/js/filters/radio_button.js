/* Constructs a radio button widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} data_column - The column of the table that the widget will filter
 * @param {Array} options - The options that the radio buttons will display
 * @param {Array} truth_values - The values that when the corresponding radio button is selected, will be filtered in
 */
class RadioButton {

    constructor(id, data_column, options, truth_values) {
        var self = this;
        const left = 0;
        self.id = id;
        self.data_column = data_column;

        let wrapper = document.getElementById(id);
        wrapper.innerHTML = "";
        wrapper.style.left = left + "px";

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

        let width = 0;
        for (let i in options) {
            let elem = document.getElementById(`${id}_${i}`);
            let opt_width = getTextWidth(options[i], elem);
            if (opt_width > width) {
                width = opt_width;
            }
        }
        self.width = width + 30;
        wrapper.style.width = self.width + "px";
    };

    reset() {
        document.getElementById(`${id}_0`).checked = true;
    };

    filter_value(value) {
        let checked = document.querySelector(`input[name=${id}]:checked`);
        let index = checked.id.split("_").pop();
        let t = truth_values[index];
        if (t instanceof Array) {
            return t.includes(value);
        }
        return value === t;
    };
};