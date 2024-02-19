// THIS IS THE RANGE SLIDER LOGIC DO NOT CHANGE !!
var DoubleRangeSlider = function(id, width, left, min, max, step) { 
  var self = this;
  var startX = 0, x = 0;
  self.width = width;
  self.left = left;
  var wrapper = document.getElementById(id);
  wrapper.style.width = width + 'px';
  wrapper.style.left = left + 'px';
  wrapper.style.position = 'relative';
  
  // retrieve touch button
  var inner_html = `<div class=slider-title id=title_${id}>${min} - ${max}</div>`
  + `<div id=widget_${id} se-min="${min}"`
  + `se-step="${step}"`
  + `se-max="${max}" class="slider"></div>`;
  wrapper.innerHTML = inner_html;
  var slider = document.getElementById(`widget_${id}`);
  slider.style.width = width + 'px';
  
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
  
  self.reset = function() {
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
  
  // initial reset
  self.reset();
  
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
          // Reset the width of the element
          self.newWidth = window.innerWidth - self.left - 50
          self.wrapper.style.width = self.newWidth + "px";
          self.slider.style.width = self.newWidth + "px";
          self.reset();
      } else if (self.slider.style.width !== self.width + "px" && window.innerWidth > self.width + self.left) {
          self.newWidth = self.width;
          self.wrapper.style.width = self.newWidth + "px";
          self.slider.style.width = self.newWidth + "px";
          self.reset();
      }
  }
  window.addEventListener("resize", function () {
      self.adjustWidth();
  });

  self.onChange = function(min, max)
  {
      document.getElementById(`title_${id}`).innerHTML = `${min} - ${max}`;
  }

  self.didChanged = function(min, max)
  {
      document.getElementById(`title_${id}`).innerHTML = `${min} - ${max}`;
  }

};