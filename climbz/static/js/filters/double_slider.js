/* Costructs a double range slider widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} title - The title of the widget
 * @param {number} step - The step size of the slider
 * @param {class} data_class - The type of data that the widget will filter, e.g. Grade, Number, Date
 * @param {string} data_column - The column of the table that the widget will filter
 */

class DoubleRangeSlider {

    constructor(id, title, step, data_class, data_column) {

        // Set the attributes of the widget
        this.id = id;
        this.data_column = data_column;
        this.title = title;
        this.data_class = data_class;
        this.data_column = data_column;

        // Define the min and max values of the slider
        let min = Infinity;
        let max = -Infinity;
        for (let climb of DATA) {
            let value = climb[data_column];
            if (value < min && value !== null)
                min = value;
            if (value > max)
                max = value;
        }
        if (min === Infinity || max === -Infinity) {
            min = 0;
            max = 0;
        }

        // Create the wrapper
        this.wrapper = document.getElementById(id);
        this.wrapper.innerHTML = "";

        // Set the title
        this.title_div = document.createElement("div");
        this.wrapper.appendChild(this.title_div);
        this.title_div.id = `title_${this.id}`;
        this.title_div.className = "mb-1";
        this.changeTitle(0, max - min);

        // Create the slider
        this.slider = document.createElement("div");
        this.wrapper.appendChild(this.slider);
        noUiSlider.create(this.slider, {
            start: [0, max - min],
            connect: true,
            range: { 'min': 0, 'max': max - min },
            step: 1,
        });
        this.slider.noUiSlider.on('update', (values, handle) => {
            this.changeTitle(parseInt(values[0]), parseInt(values[1]));
        });

    }

    reset() {
        this.slider.noUiSlider.reset();
    };

    changeTitle(min, max) {
        if (this.data_class === Grade) {
            this.title_div.innerHTML = `${this.title}: ${GRADES[min][GRADE_SCALE]} - ${GRADES[max][GRADE_SCALE]} `;
        } else {
            this.title_div.innerHTML = `${this.title}: ${min} - ${max} `;
        }
    };

    filter_value(value) {
        if (value === null)
            return false;

        let slider_values = this.slider.noUiSlider.get();
        let min = parseInt(slider_values[0]);
        let max = parseInt(slider_values[1]);
        return value >= min && value <= max;
    };
};