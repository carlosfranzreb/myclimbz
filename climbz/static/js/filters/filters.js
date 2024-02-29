function getTextWidth(text, obj) {
    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');
    context.font = getComputedStyle(obj).font; // Use the button's font style
    let width = context.measureText(text).width;
    return width;
}

/*Range slider object:
id: id of the div element to place the slider in
step: step size of the slider
*/
var DoubleRangeSlider = function(id, title, step, data_class, data_column) { 
    var self = this;
    let startX = 0, x = 0;
    self.id = id;

    self.data_column = data_column;

    let min = Infinity;
    let max = -Infinity;

    const left = 0;
    
    let get_ranges = function() {
        for (let climb of DATA){
            let value = climb[data_column];
            if (value < min) {
                min = value;
            }
            if (value > max) {
                max = value;
            }
        }
    }
    get_ranges();

    let wrapper = document.getElementById(id);
    let inner_html = `<div class=slider-title id=title_${id}>${title}: ${min} - ${max}</div>`
    + `<div id=widget_${id} se-min="${min}"`
    + `se-step="${step}"`
    + `se-max="${max}" class="double-slider"></div>`;
    wrapper.innerHTML = inner_html;

    let slider = document.getElementById(`widget_${id}`);
    inner_html = "<div class='slider-touch-left'><span></span></div>"
    + "<div class='slider-touch-right'><span></span></div>"
    + "<div class='slider-line'><span></span></div></div>";
    slider.innerHTML = inner_html;
    
    let touchLeft  = slider.querySelector('.slider-touch-left');
    let touchRight = slider.querySelector('.slider-touch-right');
    let lineSpan   = slider.querySelector('.slider-line span');

    if (step === null) {
        step = 1;
    }

    let buttonOffsetWidth = touchLeft.offsetWidth;
    let buttonWidth = buttonOffsetWidth - Number(window.getComputedStyle(touchLeft).padding.replace('px', '')*2);

    let step_width = 2*buttonWidth + 3;
    let intervals = [];
    for (let i = 0; i <= (max - min)/step + 1; i += 1) {
        intervals.push(i*step_width);
    }

    let span_width = intervals[intervals.length - 1];
    self.width = span_width + buttonOffsetWidth;


    slider.style.width = self.width + 'px';
    wrapper.style.width = self.width + 'px';
    wrapper.style.left = left + 'px';
    wrapper.style.position = 'relative';

    // retrieve default values
    let defaultMinValue = min;
    let defaultMaxValue = max;
  
    if(defaultMinValue > defaultMaxValue)
    {
        defaultMinValue = defaultMaxValue;
    }
    
    slider.setAttribute('se-min-current', defaultMinValue);
    slider.setAttribute('se-max-current', defaultMaxValue);
    

    let maxX = slider.offsetWidth - buttonOffsetWidth - buttonWidth/2;
    let selectedTouch = null;

    self.adjust_width = function(width) {
        self.width = width;
        span_width = width - buttonOffsetWidth;
        step_width = Math.floor(span_width/(intervals.length - 1));
        for (let i in intervals) {
            intervals[i] = i*step_width;
        }
        self.width = intervals[intervals.length - 1] + buttonOffsetWidth;
        maxX = width - buttonOffsetWidth - buttonWidth/2;

        slider.style.width = self.width + 'px';
        wrapper.style.width = self.width + 'px';
        self.reset();
    }
        

    // reset the slider to its default values
    self.reset = function() {
        self.setMinValue(defaultMinValue);
        slider.setAttribute('se-min-current', defaultMinValue);
        self.setMaxValue(defaultMaxValue);
        slider.setAttribute('se-max-current', defaultMaxValue);
        self.onChange(defaultMinValue, defaultMaxValue);
    }
    
    self.setMinValue = function(minValue)
    {
        let i = Math.floor((minValue - min)/step);
        touchLeft.style.left = Math.floor(intervals[i] + buttonWidth/2) + 'px';
        lineSpan.style.marginLeft = intervals[i] + 'px';
        let current_max = parseFloat(slider.getAttribute('se-max-current'));
        let j = Math.floor((current_max - min)/step);
        lineSpan.style.width = (intervals[j + 1] - intervals[i]) + 'px';
    }
    
    self.setMaxValue = function(maxValue)
    {
        let i = Math.floor((maxValue - min)/step) + 1;
        touchRight.style.left = Math.floor((intervals[i] - buttonWidth/2)) + 'px';
        let current_min = parseFloat(slider.getAttribute('se-min-current'));
        let j = Math.floor((current_min - min)/step);
        lineSpan.style.width = (intervals[i] - intervals[j]) + 'px';
    }
    
    // set defualt values
    self.setMinValue(defaultMinValue);
    self.setMaxValue(defaultMaxValue);
    
    // setup touch/click events
    function onStart(event) {
        
        // Prevent default dragging of selected content
        event.preventDefault();
        let eventTouch = event;
        
        if (event.touches)
        {
            eventTouch = event.touches[0];
        }
        
        if(this === touchLeft)
        {
            x = touchLeft.offsetLeft;
        }
        else
        {
            x = touchRight.offsetLeft;
        }
        
        startX = eventTouch.pageX - x;
        selectedTouch = this;
        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onStop);
        document.addEventListener('touchmove', onMove);
        document.addEventListener('touchend', onStop);
        
        
    }
  
    function onMove(event) {
        let eventTouch = event;
        
        if (event.touches)
        {
            eventTouch = event.touches[0];
        }
        
        x = eventTouch.pageX - startX;
        
        if (selectedTouch === touchLeft)
        {
            if(x > (touchRight.offsetLeft - buttonWidth))
            {
                x = (touchRight.offsetLeft - buttonWidth)
            }
            else if(x < buttonWidth/2)
            {
                x = buttonWidth/2;
            }
            calculateMinValue(x - buttonWidth/2);
            selectedTouch.style.left = x + 'px';
        }
        else if (selectedTouch === touchRight)
        {
            if(x < (touchLeft.offsetLeft + buttonWidth))
            {
                x = (touchLeft.offsetLeft + buttonWidth)
            }
            else if(x > maxX)
            {
                x = maxX;
            }
            calculateMaxValue(x + buttonWidth/2);
            selectedTouch.style.left = x + 'px';
        }
    
        // update line span
        lineSpan.style.marginLeft = (touchLeft.offsetLeft - buttonWidth/2) + 'px';
        lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft + buttonWidth) + 'px';
        
        
        // call on change
        if(slider.getAttribute('on-change'))
        {
            let fn = new Function('min, max', slider.getAttribute('on-change'));
            fn(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
        
        if(self.onChange)
        {
            self.onChange(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
    
    }
  
    function onStop(event) {
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup', onStop);
        document.removeEventListener('touchmove', onMove);
        document.removeEventListener('touchend', onStop);

        let eventTouch = event;
        
        if (event.touches)
        {
            eventTouch = event.touches[0];
        }
        
        x = eventTouch.pageX - startX;
        
        if (selectedTouch === touchLeft)
        {
            self.setMinValue(slider.getAttribute('se-min-current'));
            //calculateMinValue(x - buttonWidth/2);
            
        }
        else if (selectedTouch === touchRight)
        {
            self.setMaxValue(slider.getAttribute('se-max-current'));
            //calculateMaxValue(x + buttonWidth/2);

        }
        
        selectedTouch = null;
        
        
        // call did changed
        if(slider.getAttribute('did-changed'))
        {
            let fn = new Function('min, max', slider.getAttribute('did-changed'));
            fn(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
        
        if(self.didChanged)
        {
            self.didChanged(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
    }
  
    function calculateMinValue(x) {
        let minValue = Math.floor((x/step_width))*step + min;
        
        slider.setAttribute('se-min-current', minValue);
    }

    function calculateMaxValue(x) {
        let maxValue = Math.floor((x/step_width))*step + min;
        if (maxValue > max) {
            maxValue = max;
        }
        
        slider.setAttribute('se-max-current', maxValue);
    }
  
    // link events
    touchLeft.addEventListener('mousedown', onStart);
    touchRight.addEventListener('mousedown', onStart);
    touchLeft.addEventListener('touchstart', onStart);
    touchRight.addEventListener('touchstart', onStart);
  
    self.onChange = function(min, max)
    {
        if (data_class === Grade){
            document.getElementById(`title_${id}`).innerHTML = `${title}: ${GRADES[min][GRADE_SCALE]} - ${GRADES[max][GRADE_SCALE]}`;
        }
        else{
            document.getElementById(`title_${id}`).innerHTML = `${title}: ${min} - ${max}`;
        }
    }
  
    self.didChanged = function(min, max)
    {
        if (data_class === Grade){
            document.getElementById(`title_${id}`).innerHTML = `${title}: ${GRADES[min][GRADE_SCALE]} - ${GRADES[max][GRADE_SCALE]}`;
        }
        else{
            document.getElementById(`title_${id}`).innerHTML = `${title}: ${min} - ${max}`;
        }
    }
  
    self.didChanged(min, max);
    if (data_class === Grade){
        let grade_toggle = document.getElementById("grade-scale-toggle");
        grade_toggle.addEventListener("change", function () {
            self.didChanged(slider.getAttribute("se-min-current"), slider.getAttribute("se-max-current"));
        });
    }

    self.filter_value = function(value) {
        let min = parseInt(slider.getAttribute('se-min-current'));
        let max = parseInt(slider.getAttribute('se-max-current'));
        return value >= min && value <= max;
    }
};

var DropdownMenu = function(id, placeholder, data_column) {
    var self = this;
    self.left = 0;
    self.id = id;
    self.data_column = data_column;

    self.get_options = function() {
        let options = [];
        for (let climb of DATA) {
            let value = climb[data_column];
            //if value is an array, add each element to options
            if (Array.isArray(value)) {
                for (v of value) {
                    if (!options.includes(v)) {
                        options.push(v);
                    }
                }
            }
            else if (!options.includes(value)) {
                options.push(value);
            }
        }
        return options;
    }
    let options = self.get_options();
    options.unshift("Select all");
    self.options = options;
    let selected_options = [];

    self.placeholder = placeholder;
    let wrapper = document.getElementById(id);
    wrapper.style.left = self.left + 'px';
    wrapper.classList.add('btn-wrapper');
    let inner_html = `<button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>${self.placeholder}</button>`
    + `<div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>`;
    
    for (let i = 0; i < options.length; i++) {
        inner_html += `<button class='dropdown-item' id=${id}_${i}>${options[i]}</button>`;
    }
    inner_html += "</div>";
    wrapper.innerHTML = inner_html;
    let menu = document.getElementById(`${id}_menu`);
    self.menu = menu;
    self.menu.style.display = "block";
    self.menu.style.display = "none";
    let button = document.getElementById(`${id}_button`);
    self.button = button;
    self.button.addEventListener("click", openFilters);
    function openFilters() {
        self.menu.style.display =
        self.menu.style.display === "block" ? "none" : "block";
    }

    self.width = (getTextWidth(self.placeholder, self.button) + 30);
    self.button.style.width = self.width + "px";
    wrapper.style.width = self.width + "px";

    let num_selected = 0;
    let num_options = self.options.length;
    for (let i = 0; i < num_options; i++) {
        let option = document.getElementById(`${id}_${i}`);
        option.addEventListener("click", function() {
            if (self.options[i] === "Select all") {
                //change "Select all" to "Deselect all" and vice versa
                option.textContent = option.textContent === "Select all" ? "Deselect all" : "Select all";
                let all_selected = false;
                if (option.textContent === "Deselect all") {
                    all_selected = true;
                }
                selected_options = [];
                for (let j = 1; j < num_options; j++) {
                    let option = document.getElementById(`${id}_${j}`);
                    // If "Deselect all" is clicked, add a checkmark to all options
                    if (all_selected) {
                        option.classList.add('active');
                    }
                    else {
                        option.classList.remove('active');
                    }
                }
                if (all_selected) {
                    num_selected = num_options - 1;
                }
                else {
                    num_selected = 0;
                }
            }
            else {
                option.classList.toggle('active');
                if (option.classList.contains('active')) {
                    num_selected++;
                    selected_options.push(self.options[i]);
                }
                else {
                    num_selected--;
                    let index = selected_options.indexOf(self.options[i]);
                    selected_options.splice(index, 1);
                }
                if (num_selected === num_options - 1) {
                    document.getElementById(`${id}_0`).textContent = "Deselect all";
                }
                else {
                    document.getElementById(`${id}_0`).textContent = "Select all";
                } 
            }  
        });
    
    }

    //add event listener so that dropdown menu closes when element loses focus
    document.addEventListener('click', function(event) {
        if (!wrapper.contains(event.target)) {
            self.menu.style.display = "none";
        }
    });


    //reset menu to have no items selected
    self.reset = function() {
        for (let i = 0; i < options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);
            option.classList.remove('active');
        }
        document.getElementById(`${id}_0`).textContent = "Select all";
        num_selected = self.options.length - 1;
        selected_options = [];
    }

    self.filter_value = function(value) {
        if (Array.isArray(value)) {
            for (v of value) {
                //if the option with value v is active, return true
                if (selected_options.length === 0 || selected_options.includes(v)) {
                    return true;
                }
            }
            return false;
        }
        return (selected_options.length === 0 || selected_options.includes(value));
    }
}

var Checkbox = function(id, title, data_column, false_value) {
    var self = this;
    self.left = 0;
    self.id = id;
    self.data_column = data_column;
    wrapper = document.getElementById(id);
    wrapper.style.left = self.left + 'px';
    let inner_html = `
    <input class='form-check-input' type='checkbox' id='${id}_button'>
    <label class='form-check-label' for='${id}_button'>${title}</label>`;
    wrapper.innerHTML = inner_html;
    let button = document.getElementById(`${id}_button`);
    self.button = button;
    let label = document.querySelector(`label[for='${id}_button']`);
    self.width = getTextWidth(title, label) + 30;
    wrapper.style.width = self.width + "px";
    self.reset = function() {
        self.button.checked = false;
    }

    self.filter_value = function(value) {
        if (value === false_value) {
            return !self.button.checked;
        }
        else{
            return true;
        }
    }

}

var DateRange = function(id, title, data_column) {
    var self = this;
    let wrapper = document.getElementById(id);
    const left = 0;
    wrapper.style.left = left + 'px';
    self.id = id;

    self.data_column = data_column;

    let width = 100;
    self.width = width;

    let inner_html = `<div class="row">
                        <div class="col">
                            <label for="${id}_start">Start date</label>
                            <input id="${id}_start" type="text" class="form-control date-input" placeholder="DD/MM/YYYY" maxlength="10"/>
                        </div>
                        <div class="col">
                            <label for="${id}_end">End date</label>
                            <input id="${id}_end" type="text" class="form-control date-input" placeholder="DD/MM/YYYY" maxlength="10"/>
                        </div>
                    </div>`;
    
    wrapper.innerHTML = inner_html;

    let startDate = document.getElementById(`${id}_start`)
    let endDate = document.getElementById(`${id}_end`)
    let keyPressed;

    let keyDown = function(event) {
        keyPressed = event.key;
        let i = this.selectionStart-1;
        if ((event.key === "Backspace" && this.value[i] === "/")|| (event.key === "Delete" && this.value[i+1] === "/")) {
            event.preventDefault();
        }
        if (keyPressed === "ArrowLeft" && this.value[i-1] === "/") {
            this.setSelectionRange(i, i);
        }
        else if (keyPressed === "ArrowRight" && this.value[i+2] === "/") {
            this.setSelectionRange(i+2, i+2);
        }
    }

    let textInput = function () {
        //get the position of the currently entered character
        let i = this.selectionStart-1;
        if(isNaN(parseInt(this.value[i])) && keyPressed !== "Backspace" && keyPressed !== "Delete"){
            //remove the entered character if it is not a number
            this.value = this.value.slice(0, i) + this.value.slice(i+1);
            return;
        }
        let num_slashes = 0;
        for (let i = 0; i < this.value.length; i++) {
            if (this.value[i] === "/") {
                num_slashes++;
            }
        }
        if (!isNaN(parseInt(this.value[i-1])) && num_slashes < 2 && keyPressed !== "Backspace" && keyPressed !== "Delete") {
            if (!isNaN(parseInt(this.value[i-2]))){
                this.value = this.value.slice(0, i) + "/" + this.value.slice(i);
            }
            else{
                this.value = this.value.slice(0, i+1) + "/" + this.value.slice(i+1);
            }
        }
        //else if the cursor position is after a slash and backspace or the left arrow key is pressed, place the cursor before the slash
        else if (keyPressed === "Backspace" && this.value[i] === "/") {
            if (i === this.value.length-1) {
                this.setSelectionRange(i, i);
            }
            //if backspace is pressed and the slash is the last character, remove the slash
            if (i === this.value.length-1) {
                this.value = this.value.slice(0, i);
            }
        }
        else if (keyPressed === "Delete" && this.value[i] === "/" && i === this.value.length-1) {
            this.value = this.value.slice(0, i);
        }
        //check whether a slash has two numbers before it
        else if (!isNaN(parseInt(this.value[i])) && !isNaN(parseInt(this.value[i-1])) && !isNaN(parseInt(this.value[i-2])) && this.value[i+1] === "/") {
            //change the inputted number to be the first number after the slash
            this.value = this.value.slice(0, i) + "/" + this.value[i] + this.value.slice(i+2);
            this.setSelectionRange(i+2, i+2);
        }
    }
    
    startDate.addEventListener('keydown', keyDown);
    startDate.addEventListener('input', textInput);

    endDate.addEventListener('keydown', keyDown);
    endDate.addEventListener('input', textInput);


    self.reset = function() {
        startDate.value = "";
        endDate.value = "";
    }

    function parseDateString(dateString) {
        const [day, month, year] = dateString.split('/');
        // Month is 0-indexed in JavaScript, so we subtract 1 from the parsed month
        return new Date(year, month - 1, day);
    }

    self.filter_value = function(value) {
        if (startDate.value === "" || endDate.value === "") {
            if (startDate.value === "" && endDate.value === "") {
                return true;
            }
            let date;
            if (value instanceof Array) {
                date = parseDateString(value[value.length - 1]);
            }
            else{
                date = parseDateString(value);
            }
            if (startDate.value === "") {
                let end = parseDateString(endDate.value);
                return date <= end;
            }
            if (endDate.value === "") {
                let start = parseDateString(startDate.value);
                return date >= start;
            }
        }

        let start = parseDateString(startDate.value);
        let end = parseDateString(endDate.value);
        let date;
        if (value instanceof Array) {
            date = parseDateString(value[value.length - 1]);
        }
        else{
            date = parseDateString(value);
        }
        return date >= start && date <= end;
    }
}

var RadioButton = function(id, data_column, options, truth_values) {
    var self = this;
    const left = 0;
    self.id = id;
    self.data_column = data_column;

    let wrapper = document.getElementById(id);
    wrapper.innerHTML = "";
    wrapper.style.left = left + 'px';
    
    for (i in options) {
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
    for (i in options) {
        let elem = document.getElementById(`${id}_${i}`);
        let opt_width = getTextWidth(options[i], elem);
        if (opt_width > width) {
            width = opt_width;
        }
    }
    self.width = width + 30;
    wrapper.style.width = self.width + "px";

    self.reset = function() {
        document.getElementById(`${id}_0`).checked = true;
    }

    self.filter_value = function(value) {
        let checked = document.querySelector(`input[name=${id}]:checked`);
        let index = checked.id.split("_").pop();
        let t = truth_values[index];
        if (t instanceof Array) {
            return t.includes(value);
        }
        return value === t;
    }
}

var FilterWidget = function(id, left) {
    var self = this;
    self.left = left;
    self.id = id;
    wrapper = document.getElementById(id);
    wrapper.style.left = left + 'px';
    wrapper.style.width = "fit-content";
    let inner_html = `<button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>Filter</button>`
    + `<div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>`;
    //add widgets here
    let cols = {};
    for (let filter_name in window.FILTERS) {
        let row = window.FILTERS[filter_name].row;
        let col = window.FILTERS[filter_name].col;
        if (col in cols) {
            if (row in cols[col]) {
                let filter_array = [cols[col][row]];
                filter_array.push(filter_name);
                cols[col][row] = filter_array;
            }
            else{
            cols[col][row] = filter_name;
            }
        }
        else {
            cols[col] = {};
            cols[col][row] = filter_name;
        }
    }
    wrapper.innerHTML = inner_html;

    let menu = document.getElementById(`${id}_menu`);
    let row = document.createElement("div");
    row.className = "row";
    row.id = `${id}_row`;

    for (let col in cols) {
        let colElement = document.createElement("div");
        colElement.className = "col";
        colElement.id = `${id}_col_${col}`;

        for (let row in cols[col]) {
            let filter_name = cols[col][row];
            if (filter_name instanceof Array) {
                let subrow = document.createElement("div");
                subrow.className = "row";
                subrow.id = `${id}_col_${col}_subrow_${row}`;
                for (let f of filter_name) {
                    let elem = document.createElement("div");
                    elem.id = `${id}_${f}`;
                    elem.innerHTML = f;
                    subrow.appendChild(elem);
                }
                colElement.appendChild(subrow);
            }
            else {
                let elem = document.createElement("div");
                elem.id = `${id}_${filter_name}`;
                elem.innerHTML = filter_name;
                colElement.appendChild(elem);
            }

        }
        
        row.appendChild(colElement);
    }

    menu.appendChild(row);

    let col_widths = [];
    menu.style.display = "block";
    let delta = 20;
    for (let filter_name in window.FILTERS) {
        let widget = window.FILTERS[filter_name]["filter_type"];
        let filter_id = `${id}_${filter_name}`;
        if (widget === "slider") {
            let step = "step" in window.FILTERS[filter_name] ? window.FILTERS[filter_name]["step"] : null;
            FILTER_WIDGETS.push(new DoubleRangeSlider(filter_id, filter_name.replace(/_/g, " "), step, 
            window.FILTERS[filter_name]["data_class"], window.FILTERS[filter_name]["data_column"]));
        }
        else if (widget === "dropdown") {
            FILTER_WIDGETS.push(new DropdownMenu(filter_id, filter_name.replace(/_/g, " "), window.FILTERS[filter_name]["data_column"]));
        }
        else if (widget === "checkbox") {
            FILTER_WIDGETS.push(new Checkbox(filter_id, filter_name.replace(/_/g, " "), window.FILTERS[filter_name]["data_column"]));
        }
        else if (widget === "date_range") {
            FILTER_WIDGETS.push(new DateRange(filter_id, filter_name.replace(/_/g, " "), window.FILTERS[filter_name]["data_column"]));
        }
        else if (widget === "radio") {
            FILTER_WIDGETS.push(new RadioButton(filter_id, window.FILTERS[filter_name]["data_column"], window.FILTERS[filter_name]["options"], window.FILTERS[filter_name]["truth_values"]));
        }
        let widgetWidth = Math.floor(FILTER_WIDGETS[FILTER_WIDGETS.length - 1].width);
        let current_col = window.FILTERS[filter_name]["col"];
        if (col_widths[current_col] === undefined) {
            col_widths[current_col] = widgetWidth + delta;
        }
        else {
            col_widths[current_col] = Math.max(col_widths[current_col], widgetWidth + delta);
        }
    }
    for (let w in col_widths) {
        let col = document.getElementById(`${id}_col_${w}`);
        col.style.width = `${col_widths[w]}px`;
    }

    for (let filter of FILTER_WIDGETS) {
        let filter_name = filter.id.split("_")[1];
        if (window.FILTERS[filter_name]["filter_type"] === "slider") {
            if (filter.width < col_widths[window.FILTERS[filter_name]["col"]] - delta){
                filter.adjust_width(col_widths[window.FILTERS[filter_name]["col"]] - delta);
            }
        }
    }
    
    let divider = document.createElement("div");
    divider.className = "dropdown-divider";
    menu.appendChild(divider);

    let bottom_row = document.createElement("div");
    bottom_row.className = "row";
    bottom_row.id = `${id}_bottom_row`;

    let filter_apply = document.createElement("button");
    filter_apply.className = "btn btn-primary";
    filter_apply.id = "filter_apply";
    filter_apply.type = "button";
    filter_apply.innerHTML = "Apply";
    bottom_row.appendChild(filter_apply);

    let filter_reset = document.createElement("button");
    filter_reset.className = "btn btn-primary";
    filter_reset.id = "filter_reset";
    filter_reset.type = "button";
    filter_reset.innerHTML = "Reset";
    bottom_row.appendChild(filter_reset);

    menu.appendChild(bottom_row);

    self.menu = menu;

    self.menu.style.display = "none";
    let filter_button = document.getElementById(`${id}_button`);
    self.filter_button = filter_button;
    self.filter_button.addEventListener("click", openFilters);
    function openFilters() {
        self.menu.style.display =
        self.menu.style.display === "block" ? "none" : "block";
    }

    // Reset all filters when the reset button is clicked
    filter_reset.addEventListener("click", function() {
        for (let i = 0; i < FILTER_WIDGETS.length; i++) {
            FILTER_WIDGETS[i].reset();
        }
    });

    // Apply filters when the apply button is clicked
    filter_apply.addEventListener("click", function() {
        display_data();
        self.menu.style.display = "none";
    });

    document.addEventListener('click', function(event) {
        if (!wrapper.contains(event.target)) {
            self.menu.style.display = "none";
        }
    });
}