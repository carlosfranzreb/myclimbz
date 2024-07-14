/* Constructs a date range widget
 * @param {string} id - The id of the div wrapper that contains the widget
 * @param {string} title - The title of the widget
 * @param {string} data_column - The column of the table that the widget will filter
 */
var DateRange = function (id, title, data_column) {
    var self = this;
    let wrapper = document.getElementById(id);
    const left = 0;
    wrapper.style.left = left + "px";
    self.id = id;

    self.data_column = data_column;

    self.width = 100;

    let inner_html = `<div class="row">
                        <div class="col" id="${id}_start_col">
                            <label for="${id}_start">Start date</label>
                            <input id="${id}_start" type="text" class="form-control date-input" placeholder="DD/MM/YYYY" maxlength="10"/>
                        </div>
                        <div class="col" id="${id}_end_col">
                            <label for="${id}_end">End date</label>
                            <input id="${id}_end" type="text" class="form-control date-input" placeholder="DD/MM/YYYY" maxlength="10"/>
                        </div>
                    </div>`;

    wrapper.innerHTML = inner_html;

    document.getElementById(`${id}_start_col`).style.margin = "0px";
    document.getElementById(`${id}_end_col`).style.margin = "0px";

    let startDate = document.getElementById(`${id}_start`);
    let endDate = document.getElementById(`${id}_end`);
    let keyPressed;

    // Sets or removes a "/" when appropriate
    let backslashAid = function (event) {
        keyPressed = event.key;
        let i = this.selectionStart - 1;
        if (
            (event.key === "Backspace" && this.value[i] === "/") ||
            (event.key === "Delete" && this.value[i + 1] === "/")
        ) {
            event.preventDefault();
        }
        if (keyPressed === "ArrowLeft" && this.value[i - 1] === "/") {
            this.setSelectionRange(i, i);
        } else if (keyPressed === "ArrowRight" && this.value[i + 2] === "/") {
            this.setSelectionRange(i + 2, i + 2);
        }
    };

    let validateInput = function () {
        //get the position of the currently entered character
        let i = this.selectionStart - 1;
        if (
            isNaN(parseInt(this.value[i])) &&
            keyPressed !== "Backspace" &&
            keyPressed !== "Delete"
        ) {
            //remove the entered character if it is not a number
            this.value = this.value.slice(0, i) + this.value.slice(i + 1);
            return;
        }
        let num_slashes = 0;
        for (let i = 0; i < this.value.length; i++) {
            if (this.value[i] === "/") {
                num_slashes++;
            }
        }
        if (
            !isNaN(parseInt(this.value[i - 1])) &&
            num_slashes < 2 &&
            keyPressed !== "Backspace" &&
            keyPressed !== "Delete"
        ) {
            if (!isNaN(parseInt(this.value[i - 2]))) {
                this.value = this.value.slice(0, i) + "/" + this.value.slice(i);
            } else {
                this.value = this.value.slice(0, i + 1) + "/" + this.value.slice(i + 1);
            }
        }
        //else if the cursor position is after a slash and backspace or the left arrow key is pressed, place the cursor before the slash
        else if (keyPressed === "Backspace" && this.value[i] === "/") {
            if (i === this.value.length - 1) {
                this.setSelectionRange(i, i);
            }
            //if backspace is pressed and the slash is the last character, remove the slash
            if (i === this.value.length - 1) {
                this.value = this.value.slice(0, i);
            }
        } else if (
            keyPressed === "Delete" &&
            this.value[i] === "/" &&
            i === this.value.length - 1
        ) {
            this.value = this.value.slice(0, i);
        }
        //check whether a slash has two numbers before it
        else if (
            !isNaN(parseInt(this.value[i])) &&
            !isNaN(parseInt(this.value[i - 1])) &&
            !isNaN(parseInt(this.value[i - 2])) &&
            this.value[i + 1] === "/"
        ) {
            //change the inputted number to be the first number after the slash
            this.value =
                this.value.slice(0, i) + "/" + this.value[i] + this.value.slice(i + 2);
            this.setSelectionRange(i + 2, i + 2);
        }
    };

    startDate.addEventListener("backslashAid", backslashAid);
    startDate.addEventListener("input", validateInput);

    endDate.addEventListener("backslashAid", backslashAid);
    endDate.addEventListener("input", validateInput);

    self.reset = function () {
        startDate.value = "";
        endDate.value = "";
    };

    function parseDateString(dateString) {
        if (dateString === "" || dateString === null) {
            return null;
        }
        const [day, month, year] = dateString.split("/");
        // Month is 0-indexed in JavaScript, so we subtract 1 from the parsed month
        return new Date(year, month - 1, day);
    }

    self.filter_value = function (value) {
        let start = parseDateString(startDate.value);
        let end = parseDateString(endDate.value);
        let date;
        //! If many dates are selected, use the last date
        if (value instanceof Array) {
            date = parseDateString(value[value.length - 1]);
        } else {
            date = parseDateString(value);
        }
        if (start === null || end === null) {
            if (start === null && end === null) {
                return true;
            }
            if (date === null) {
                return false;
            }
            if (start === null) {
                return date <= end;
            }
            if (end === null) {
                return date >= start;
            }
        }
        if (date === null) {
            return false;
        }
        return date >= start && date <= end;
    };
};