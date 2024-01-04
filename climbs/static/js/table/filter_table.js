// THIS IS THE RANGE SLIDER LOGIC DO NOT CHANGE !!
var DoubleRangeSlider = function(id, width, left) { 
  var self = this;
  var startX = 0, x = 0;
  self.width = width;
  self.left = left;

  // retrieve touch button
  var slider = document.getElementById(id)
  slider.style.width = width + 'px';
  slider.style.left = left + 'px';
  var inner_html = "<div class='slider-touch-left'><span></span></div>"
  + "<div class='slider-touch-right'><span></span></div>"
  + "<div class='slider-line'><span></span></div></div>";
  slider.innerHTML = inner_html;

  var touchLeft  = slider.querySelector('.slider-touch-left');
  var touchRight = slider.querySelector('.slider-touch-right');
  var lineSpan   = slider.querySelector('.slider-line span');

  // get some properties
  var min   = parseFloat(slider.getAttribute('se-min'));
  var max   = parseFloat(slider.getAttribute('se-max'));

  // retrieve default values
  var defaultMinValue = min;
  if(slider.hasAttribute('se-min-value'))
  {
    defaultMinValue = parseFloat(slider.getAttribute('se-min-value'));  
  }
  var defaultMaxValue = max;

  if(slider.hasAttribute('se-max-value'))
  {
    defaultMaxValue = parseFloat(slider.getAttribute('se-max-value'));  
  }

  // check values are correct
  if(defaultMinValue < min)
  {
    defaultMinValue = min;
  }

  if(defaultMaxValue > max)
  {
    defaultMaxValue = max;
  }

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
  var normalizeFact = 26;

  self.slider = slider;
  var left_button_x, right_button_x;
  self.reset = function() {
    left_button_x = Math.floor((parseInt(touchLeft.style.left, 10))*self.newWidth/(self.widthChange + self.newWidth));
    right_button_x = Math.floor((parseInt(touchRight.style.left, 10))*self.newWidth/(self.widthChange + self.newWidth));
    touchLeft.style.left = left_button_x + 'px';
    touchRight.style.left = right_button_x + 'px';
    lineSpan.style.marginLeft = left_button_x + 'px';
    lineSpan.style.width = right_button_x - left_button_x + 'px';
    startX = 0;
    x = 0;
  };

  self.setMinValue = function(minValue)
  {
    var ratio = ((minValue - min) / (max - min));
    touchLeft.style.left = Math.ceil(ratio * (slider.offsetWidth - (touchLeft.offsetWidth + normalizeFact))) + 'px';
    lineSpan.style.marginLeft = touchLeft.offsetLeft + 'px';
    lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft) + 'px';
    slider.setAttribute('se-min-value', minValue);
  }

  self.setMaxValue = function(maxValue)
  {
    var ratio = ((maxValue - min) / (max - min));
    touchRight.style.left = Math.ceil(ratio * (slider.offsetWidth - (touchLeft.offsetWidth + normalizeFact)) + normalizeFact) + 'px';
    lineSpan.style.marginLeft = touchLeft.offsetLeft + 'px';
    lineSpan.style.width = (touchRight.offsetLeft - touchLeft.offsetLeft) + 'px';
    slider.setAttribute('se-max-value', maxValue);
  }

  // initial reset
  self.reset();

  // usefull values, min, max, normalize fact is the width of both touch buttons
  var maxX = slider.offsetWidth - touchRight.offsetWidth;
  var selectedTouch = null;
  var initialValue = (lineSpan.offsetWidth - normalizeFact);

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
      fn(slider.getAttribute('se-min-value'), slider.getAttribute('se-max-value'));
    }
    
    if(self.onChange)
    {
      self.onChange(slider.getAttribute('se-min-value'), slider.getAttribute('se-max-value'));
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
      fn(slider.getAttribute('se-min-value'), slider.getAttribute('se-max-value'));
    }
    
    if(self.didChanged)
    {
      self.didChanged(slider.getAttribute('se-min-value'), slider.getAttribute('se-max-value'));
    }
  }

  function calculateValue() {
    var newValue = (lineSpan.offsetWidth - normalizeFact) / initialValue;
    var minValue = lineSpan.offsetLeft / initialValue;
    var maxValue = minValue + newValue;

    var minValue = minValue * (max - min) + min;
    var maxValue = maxValue * (max - min) + min;
    
    if (step !== 0.0)
    {
      var multi = Math.floor((minValue / step));
      minValue = step * multi;
      
      multi = Math.floor((maxValue / step));
      maxValue = step * multi;
    }
    
    slider.setAttribute('se-min-value', minValue);
    slider.setAttribute('se-max-value', maxValue);
  }

  // link events
  touchLeft.addEventListener('mousedown', onStart);
  touchRight.addEventListener('mousedown', onStart);
  touchLeft.addEventListener('touchstart', onStart);
  touchRight.addEventListener('touchstart', onStart);
  var newWidth;
  var widthChange;
  self.widthChange = widthChange;
  self.newWidth = newWidth;

  self.adjustWidth = function() {
    // Check if the right edge of the element is past the right edge of the window
    if (self.left+self.width + 50 > window.innerWidth) {
        // Reset the width of the element
        self.newWidth = window.innerWidth - self.left - 50
        self.widthChange = parseInt(self.slider.style.width, 10) - self.newWidth;
        self.slider.style.width = self.newWidth + "px";
        self.reset();
    } else if (self.slider.style.width !== self.width + "px" && window.innerWidth > self.width + self.left) {
        self.newWidth = self.width;
        self.widthChange = parseInt(self.slider.style.width, 10) - self.newWidth;
        self.slider.style.width = self.newWidth + "px";
        self.reset();
    }
  }
  window.addEventListener("resize", function () {
    self.adjustWidth();
  });

  self.onChange = function(min, max)
  {
    document.getElementById("result_slider_1").innerHTML = 'Min: ' + min + ' Max: ' + max;
  }
    
  self.didChanged = function(min, max)
  {
    document.getElementById("result_slider_1").innerHTML = 'Min: ' + min + ' Max: ' + max;
  }

};