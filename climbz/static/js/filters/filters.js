FILTERS = {
    "Grade":{"row": 0, "col": 0, "type": "slider", "params": [ "Grade", 0, 1, 10, 1]},
    "Inclination":{"row": 1, "col": 0, "type": "slider", "params": [ "Inclination", 0, "min", "max", 5]},
    "Landing":{"row": 0, "col": 1, "type": "slider", "params": [ "Landing", 0, 1, 10, 1]},
    "Height":{"row": 1, "col": 1, "type": "slider", "params": [ "Height", 0, 1, 10, 1]},
    "Area":{"row": 2, "col": 0, "type": "dropdown", "params": [ "Area", 0, ["good", "bad", "ugly"]]},
    "Style":{"row": 2, "col": 1, "type": "dropdown", "params": [ "Style", 0, ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]]},
    "Sit_start":{"row": 3, "col": 0, "type": "checkbox", "params": [ "Sit start", 0]},
    "Projects":{"row": 4, "col": 0, "type": "checkbox", "params": [ "Projects", 0]},
    "Sends":{"row": 3, "col": 1, "type": "checkbox", "params": [ "Sends", 0]},
    "Attempted":{"row": 4, "col": 1, "type": "checkbox", "params": [ "Attempted", 0]},
    //"Date": add_filter_range,
    //"Tries": add_filter_range,
}


function getTextWidth(text, obj) {
    let canvas = document.createElement('canvas');
    let context = canvas.getContext('2d');
    context.font = getComputedStyle(obj).font; // Use the button's font style
    let width = context.measureText(text).width;
    return width;
}

/*Range slider object:
id: id of the div element to place the slider in
left: left offset of the slider
min: minimum value of the slider
max: maximum value of the slider
step: step size of the slider
*/
var DoubleRangeSlider = function(id, title, left, min, max, step) { 
    var self = this;
    var startX = 0, x = 0;
    //Assumes that "max" also wanted
    if (min === "min") {
        //Find minimum value in the data
        [min, max] = window.data_table.columns().get_min_max(title);
    }
    self.width = 15*(max - min)/step;
    self.left = left;
    self.title = title;
    var wrapper = document.getElementById(id);
    wrapper.style.width = self.width + 'px';
    wrapper.style.left = left + 'px';
    wrapper.style.position = 'relative';


    
    // retrieve touch button
    var inner_html = `<div class=slider-title id=title_${id}>${self.title}: ${min} - ${max}</div>`
    + `<div id=widget_${id} se-min="${min}"`
    + `se-step="${step}"`
    + `se-max="${max}" class="double-slider"></div>`;
    wrapper.innerHTML = inner_html;
    var slider = document.getElementById(`widget_${id}`);
    slider.style.width = self.width + 'px';
    
    inner_html = "<div class='slider-touch-left'><span></span></div>"
    + "<div class='slider-touch-right'><span></span></div>"
    + "<div class='slider-line'><span></span></div></div>";
    slider.innerHTML = inner_html;
    
    self.wrapper = wrapper;
    self.slider = slider;
    var touchLeft  = slider.querySelector('.slider-touch-left');
    var touchRight = slider.querySelector('.slider-touch-right');
    var lineSpan   = slider.querySelector('.slider-line span');
    
    // retrieve default values
    var defaultMinValue = min;
    var defaultMaxValue = max;
  
    if(defaultMinValue > defaultMaxValue)
    {
        defaultMinValue = defaultMaxValue;
    }
    
    var step  = 0.0;
    
    if (slider.getAttribute('se-step'))
    {
        step  = Math.abs(parseFloat(slider.getAttribute('se-step')));
    }
    
    // normalize flag
    
    self.slider.setAttribute('se-min-current', defaultMinValue);
    self.slider.setAttribute('se-max-current', defaultMaxValue);
    
    var left_button_x, right_button_x, current_min, current_max;
    var newWidth = self.width;
    self.newWidth = newWidth;
    self.buttonWidth = parseInt(window.getComputedStyle(touchLeft)["width"]);

    // reset the slider to its default values
    self.reset = function() {
        self.setMinValue(defaultMinValue);
        self.setMaxValue(defaultMaxValue);
        self.slider.setAttribute('se-min-current', defaultMinValue);
        self.slider.setAttribute('se-max-current', defaultMaxValue);
        self.onChange(defaultMinValue, defaultMaxValue);
    }

    
    self.readjust = function() {
        current_min = parseInt(slider.getAttribute('se-min-current'));
        current_max = parseInt(slider.getAttribute('se-max-current'));
        left_button_x = Math.floor((self.newWidth-self.buttonWidth)*(current_min - min)/(max - min));
        right_button_x = Math.floor((self.newWidth-self.buttonWidth)*(current_max - min)/(max - min));
        if (left_button_x === right_button_x) {
            if (left_button_x <= 50) {
                right_button_x += self.buttonWidth;
            }
            else{
                left_button_x -= self.buttonWidth;
            }
        }
        touchLeft.style.left = left_button_x + 'px';
        touchRight.style.left = right_button_x + 'px';
        lineSpan.style.marginLeft = left_button_x + 'px';
        lineSpan.style.width = right_button_x - left_button_x + 'px';
        startX = 0;
        x = 0;
        maxX = slider.offsetWidth - touchRight.offsetWidth;
        line_max_width = (self.newWidth - self.buttonWidth );
    };
    
    self.setMinValue = function(minValue)
    {
        var ratio = ((minValue - min) / (max - min));
        touchLeft.style.left = Math.ceil(ratio * (slider.offsetWidth - (touchLeft.offsetWidth ))) + 'px';
        lineSpan.style.marginLeft = touchLeft.offsetLeft + 'px';
        lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft) + 'px';
    }
    
    self.setMaxValue = function(maxValue)
    {
        var ratio = ((maxValue - min) / (max - min));
        touchRight.style.left = Math.ceil(ratio * (slider.offsetWidth - (touchLeft.offsetWidth )) ) + 'px';
        lineSpan.style.marginLeft = touchLeft.offsetLeft + 'px';
        lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft) + 'px';
    }
    
    // initial readjust
    self.readjust();
    
    // usefull values, min, max, normalize fact is the width of both touch buttons
    var maxX = slider.offsetWidth - touchRight.offsetWidth;
    var selectedTouch = null;
    var line_max_width = (lineSpan.offsetWidth );
    
    // set defualt values
    self.setMinValue(defaultMinValue);
    self.setMaxValue(defaultMaxValue);
    
    // setup touch/click events
    function onStart(event) {
        
        // Prevent default dragging of selected content
        event.preventDefault();
        var eventTouch = event;
        
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
        var eventTouch = event;
        
        if (event.touches)
        {
            eventTouch = event.touches[0];
        }
        
        x = eventTouch.pageX - startX;
        
        if (selectedTouch === touchLeft)
        {
            if(x > (touchRight.offsetLeft - selectedTouch.offsetWidth + 10))
            {
                x = (touchRight.offsetLeft - selectedTouch.offsetWidth + 10)
            }
            else if(x < 0)
            {
                x = 0;
            }
            
            selectedTouch.style.left = x + 'px';
        }
        else if (selectedTouch === touchRight)
        {
            if(x < (touchLeft.offsetLeft + touchLeft.offsetWidth - 10))
            {
                x = (touchLeft.offsetLeft + touchLeft.offsetWidth - 10)
            }
            else if(x > maxX)
            {
                x = maxX;
            }
        selectedTouch.style.left = x + 'px';
    }
    
    // update line span
    lineSpan.style.marginLeft = touchLeft.offsetLeft + 'px';
    lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft) + 'px';
    
    // write new value
    calculateValue();
    
    // call on change
    if(slider.getAttribute('on-change'))
    {
        var fn = new Function('min, max', slider.getAttribute('on-change'));
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
        
        selectedTouch = null;
        
        // write new value
        calculateValue();
        
        // call did changed
        if(slider.getAttribute('did-changed'))
        {
            var fn = new Function('min, max', slider.getAttribute('did-changed'));
            fn(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
        
        if(self.didChanged)
        {
            self.didChanged(slider.getAttribute('se-min-current'), slider.getAttribute('se-max-current'));
        }
    }
  
    function calculateValue() {
        var newValue = (lineSpan.offsetWidth ) / line_max_width;
        var minValue = lineSpan.offsetLeft / line_max_width;
        var maxValue = minValue + newValue;
        
        var minValue = minValue * (max - min) + min;
        var maxValue = maxValue * (max - min) + min;
        
        if (step !== 0.0)
        {
            var multi = Math.round((minValue / step));
            minValue = step * multi;
            
            multi = Math.round((maxValue / step));
            maxValue = step * multi;
        }
        
        slider.setAttribute('se-min-current', minValue);
        slider.setAttribute('se-max-current', maxValue);
    }
  
    // link events
    touchLeft.addEventListener('mousedown', onStart);
    touchRight.addEventListener('mousedown', onStart);
    touchLeft.addEventListener('touchstart', onStart);
    touchRight.addEventListener('touchstart', onStart);
  
    self.adjustWidth = function() {
        // Check if the right edge of the element is past the right edge of the window
        if (self.left+self.width + 50 > window.innerWidth) {
            // readjust the width of the element
            self.newWidth = window.innerWidth - self.left - 50
            self.wrapper.style.width = self.newWidth + "px";
            self.slider.style.width = self.newWidth + "px";
            self.readjust();
        } else if (self.slider.style.width !== self.width + "px" && window.innerWidth > self.width + self.left) {
            self.newWidth = self.width;
            self.wrapper.style.width = self.newWidth + "px";
            self.slider.style.width = self.newWidth + "px";
            self.readjust();
        }
    }
    window.addEventListener("resize", function () {
        self.adjustWidth();
    });
  
    self.onChange = function(min, max)
    {
        document.getElementById(`title_${id}`).innerHTML = `${self.title}: ${min} - ${max}`;
    }
  
    self.didChanged = function(min, max)
    {
        document.getElementById(`title_${id}`).innerHTML = `${self.title}: ${min} - ${max}`;
    }
  
  };

var DropdownMenu = function(id, placeholder, left, options) {
    var self = this;
    self.left = left;
    self.id = id;
    options.unshift("Select all");
    self.options = options;
    self.placeholder = placeholder;
    var wrapper = document.getElementById(id);
    wrapper.style.left = left + 'px';
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
                }
                else {
                    num_selected--;
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


    //reset menu to have no items selected
    self.reset = function() {
        for (let i = 0; i < options.length; i++) {
            let option = document.getElementById(`${id}_${i}`);
            option.classList.remove('active');
        }
    }
}

var Checkbox = function(id, title, left) {
    var self = this;
    self.left = left;
    self.id = id;
    wrapper = document.getElementById(id);
    wrapper.style.left = left + 'px';
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
}

var FilterWidget = function(id, left) {
    var self = this;
    self.left = left;
    self.id = id;
    wrapper = document.getElementById(id);
    wrapper.style.left = left + 'px';
    let inner_html = `<button class='btn btn-secondary dropdown-toggle' type='button' id='${id}_button' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>Filter</button>`
    + `<div class='dropdown-menu' aria-labelledby='${id}_button' id='${id}_menu'>`;
    //add widgets here
    let cols = {};
    for (let filter_name in window.FILTERS) {
        let row = window.FILTERS[filter_name].row;
        let col = window.FILTERS[filter_name].col;
        if (col in cols) {
            cols[col][row] = filter_name;
        }
        else {
            cols[col] = {};
            cols[col][row] = filter_name;
        }
        //inner_html += `<div id=${id}_${filter_name}>${filter_name}</div>`;  
    }
    let col_width = Math.floor(12/Object.keys(cols).length);
    wrapper.innerHTML = inner_html;
    let menu = document.getElementById(`${id}_menu`);
    let row = document.createElement("div");
    row.className = "row";
    row.id = `${id}_row`;

    var widgets = [];
    // Calculate the width for each column
    for (let col in cols) {
        let colElement = document.createElement("div");
        colElement.className = "col";
        colElement.id = `${id}_col_${col}`;

        for (let row in cols[col]) {
            let filter_name = cols[col][row];
            colElement.innerHTML += `<div id=${id}_${filter_name}>${filter_name}</div>`;

        }
        
        row.appendChild(colElement);
    }

    menu.appendChild(row);

    var widgets = [];
    var col_widths = [];
    menu.style.display = "block";
    for (let filter_name in window.FILTERS) {
        let filter_settings = window.FILTERS[filter_name]["params"];
        let widget = window.FILTERS[filter_name]["type"];
        let filter_id = `${id}_${filter_name}`;
        if (widget === "slider") {
            widgets.push(new DoubleRangeSlider(filter_id, ...filter_settings));
        }
        else if (widget === "dropdown") {
            widgets.push(new DropdownMenu(filter_id, ...filter_settings));
        }
        else if (widget === "checkbox") {
            widgets.push(new Checkbox(filter_id, ...filter_settings));
        }
        let widgetWidth = Math.floor(widgets[widgets.length - 1].width);
        let current_col = window.FILTERS[filter_name]["col"];
        if (col_widths[current_col] === undefined) {
            col_widths[current_col] = widgetWidth + 20;
        }
        else {
            col_widths[current_col] = Math.max(col_widths[current_col], widgetWidth + 20);
        }
    }
    for (let w in col_widths) {
        let col = document.getElementById(`${id}_col_${w}`);
        col.style.width = `${col_widths[w]}px`;
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
        for (let i = 0; i < widgets.length; i++) {
            widgets[i].reset();
        }
    });

    // Apply filters when the apply button is clicked
    filter_apply.addEventListener("click", function() {
        // Apply filters
        // plot_data();
    });
}