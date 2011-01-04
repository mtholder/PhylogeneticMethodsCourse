var DEBUGGING = false;
YUI({debug : DEBUGGING}).use("event-key", "widget", 'console', 'slider','node', function(Y) {

// load a console in debug mode, so we see the Y.log messages
if (DEBUGGING) {
	new Y.Console({height : 900}).render();
}
// write all of the non-function properties of an object to the log opts = {prefix : '', level : 'info'}
function logObjectData(o, f, opts) {
	var lines = []
	for (a in o) {
		if (!(typeof o[a] === 'function')) {
			lines[lines.length] = String(a) + " = " + String(o[a]);
		}
	}
	var p = opts.prefix || '';
	var level = opts.level || 'info';
	f(p + 'Object : ' + o + '\n	 ' + lines.join('\n	 '), level);
}

// write all of the properties of an object to the log opts = {prefix : '', level : 'info'}
function logObject(o, f, opts) {
	var lines = []
	for (a in o) {
		lines[lines.length] = String(a) + " = " + String(o[a]);
	}
	var p = opts.prefix || '';
	var level = opts.level || 'info';
	f(p + 'Object : ' + o + '\n	 ' + lines.join('\n	 '), level);
}
// log an exception to function f
function logException(e, f) {
	try {
		var st = printStackTrace({e : e});
		f("Exception: name=" + e.name + ' message=' + e.message +  '\n' + st.join('\n  '), "error");
	}
	catch (ex) {
		logObject(e, f, {prefix : 'Exception without stacktrace'});
		logObject(ex, f, {prefix : 'Exception during stacktrace'});
	}
}

// returns false if o is null or undefined
function isNone(o) {
	return (o === null || o === undefined);
}
// returns false if o is null or undefined
function isNotNone(o) {
	return !(o === null || o === undefined);
}
// takes a collection of key values, and returns all of the keys that don't have
//	values that are undefined or null
function getNotNonePairs(o, keyList) {
	var r = {};
	var v;
	if (Y.Lang.isArray(keyList)) {
		for (var a in keyList) {
			v = o[a]
			if (isNotNone(v)) {
				r[a] = v;
			}
		}
	}
	else {
		for (var a in o) {
			v = o[a]
			if (isNotNone(v)) {
				r[a] = v;
			}
		}
	}
	return r
}
	var Widget = Y.Widget;
	var Node = Y.Node;



//Y.log("starting to declare DualInputSlider");
// ctor...
function DualInputSlider(config) {
	DualInputSlider.superclass.constructor.apply(this, arguments);
}
DualInputSlider.NAME = "dualInputSlider"; // required for Widget classes and used as event prefix
DualInputSlider.SETABLE_ATTRS = ['min', 'max', 'value', 'minorStep', 'majorStep' ]; // mth convention for attrs that may be in the ctor config
DualInputSlider.ATTRS = {
	min :	{ value : 0 },
	max :	{ value : 100},
	value : { value : null,
			  validator : function(val) {
					return this._validateValue(val);
				}
			},
	minorStep : { value : 1},
	majorStep : { value : 10},
	sliderLength : { value : 150},
	strings:	{ value :	{
						tooltip: "Press the arrow up/down keys for minor increments, page up/down for major increments.",
						slider: "Slider"
					}
				}
};

// identifies the classname applied to the value field
DualInputSlider.INPUT_CLASS = Y.ClassNameManager.getClassName(DualInputSlider.NAME, "value");

// used to create DualInputSlider DOM elements 
DualInputSlider.INPUT_TEMPLATE = '<input type="text" class="' + DualInputSlider.INPUT_CLASS + '">';
//DualInputSlider.BTN_TEMPLATE = '<button type="button"></button>';
DualInputSlider.SLIDER_TEMPLATE = '<span class="horiz_slider"></span>';

// Used to configure widget frome the value html attribute on the markup on the page
DualInputSlider.HTML_PARSER = {
	value: function (srcNode) {
		var val = +srcNode.get("value"); 
		//Y.log("In HTML_PARSER val= " + val); 
		return (Y.Lang.isNumber(val) ? val : null);
	}
};
Y.extend(DualInputSlider, Widget, {
		initializer: function(config) {
			//logObject(config, Y.log, {level:'info', prefix: 'in initializer(config).  config is:'});

			// \todo the following code should go in a hook triggered when max, min, or sliderLength change (except it shouldn't raise exception there....)

			this.valueMax = this.get('max'); 
			this.valueMin = this.get('min');
			if (isNone(this.valueMax) || isNone(this.valueMin) || (this.valueMax < this.valueMin)) {
				throw {name : 'Error' , message : 'DualInputSlider max must be >= min'};
			}
			this.valueRange = this.valueMax - this.valueMin;
			this.slider2InputDenom = 10000;
			this.sliderMin = 0.0;
			this.sliderMax = this.sliderMin + this.slider2InputDenom*this.valueRange;
			// Create a horizontal Slider using all defaults
			const configVi = this.get('value');
			const valueInitial = (isNone(configVi) ? this.valueMin + 0.1*this.valueRange : configVi);
			this.sliderInitial = this.sliderMin + this.slider2InputDenom*(valueInitial - this.valueMin);
			if (isNone(this.get('sliderLength')) || this.get('sliderLength') < 0)	 {
				this.set('sliderLength', 200);
			}
			this.sliderBinSize = 1/this.get('sliderLength');
			if (valueInitial != configVi) {
				this.set('value', valueInitial);
			}

		},

		destructor : function() {
			//Y.log('in destructor');
			this._documentMouseUpHandle.detach();

			this.inputNode = null;
			this.slider = null;
		},

		renderUI : function() {
			//Y.log('in renderUI');
			this._renderSlider();
			this._renderInput();
		},

		bindUI : function() {
			//Y.log('in bindUI');
			this.after("valueChange", this._afterValueChange);
			var boundingBox = this.get("boundingBox");

			// Looking for a key event which will fire continously across browsers while the key is held down. 38, 40 = arrow up/down, 33, 34 = page up/down
			var keyEventSpec = (!Y.UA.opera) ? "down:" : "press:";
			keyEventSpec += "38, 40, 33, 34";

			Y.on("key", Y.bind(this._onDirectionKey, this), boundingBox, keyEventSpec);
			Y.on("change", Y.bind(this._onInputChange, this), this.inputNode);
			this.slider.after( "valueChange", Y.bind(this._afterSliderChange, this), boundingBox );
			Y.on("keyup", Y.bind(this._onKeyUp, this), boundingBox );


		},

		syncUI : function() {
			//Y.log('in syncUI');
			this._uiSetValue(this.get("value"));
		},

		_renderInput : function() {
			//Y.log('in renderInput');
			var contentBox = this.get("contentBox"),
				input = contentBox.one("." + DualInputSlider.INPUT_CLASS),
				strings = this.get("strings");

			if (!input) {
				input = Node.create(DualInputSlider.INPUT_TEMPLATE);
				contentBox.appendChild(input);
			}

			input.set("title", strings.tooltip);
			this.inputNode = input;
			this.inputNode.setData( { slider: this.slider} );

		},

		_renderSlider : function() {
			//Y.log('in renderSlider');
			var contentBox = this.get("contentBox");
			var strings = this.get("strings");

			var inc = this._createSlider(strings.slider, this.getClassName("horiz_slider"));
			this.sliderNode = contentBox.appendChild(inc);
			// Render the Slider next to the input
			this.slider.render(inc);
		  },

		_createSlider : function(text, className) {
			var btn = Y.Node.create(DualInputSlider.SLIDER_TEMPLATE);
			//btn.set("innerHTML", text);
			btn.set("title", text);
			btn.addClass(className);
			this.slider = new Y.Slider({value : this.sliderInitial, max : this.sliderMax, length : this.get('sliderLength')});
			return btn;
		 },

		_defaultCB : function() {
			return null;
		},

		// Increments/Decrement the input value, based on the key pressed.
		_onDirectionKey : function(e) {
			//Y.log('in _onDirectionKey');
			e.preventDefault();
			var currVal = this.get("value");
			var newVal = +currVal;
			var minorStep = +this.get("minorStep");
			var majorStep = +this.get("majorStep");

			switch (e.charCode) {
				case 38:
					newVal += minorStep;
					break;
				case 40:
					newVal -= minorStep;
					break;
				case 33:
					newVal += majorStep;
					break;
				case 34:
					newVal -= majorStep;
					break;
			}
			newVal = Math.min(newVal, +this.get("max"));
			newVal = Math.max(newVal, +this.get("min"));
			if (newVal !== currVal) {
				this.set("value", newVal);
			}
		},

		// updates self from the inputNode if needed, or sets the inputnode back to a legal value
		_onInputChange : function(e) {
			//Y.log('in _onInputChange');
			var iv = this.inputNode.get("value");
			if (!this._validateValue(iv)) {
				this.inputNode.setStyle("color", "red");
				this.syncUI();
			}
			else {
				this.inputNode.setStyle("color", "black");
				this.set('value', iv);
			}
		},


		_onKeyUp : function (e) {
			//Y.log('in _onKeyUp');

			switch (e.charCode) {
				case 38:
				case 40:
				case 33:
				case 34:
					return;
			}
			//Y.log('in _onKeyUp not a DirectionKey');
			//logObjectData(e, Y.log, {prefix: 'event'});
			
			this._onInputChange(e);

		},
		// If the slider has moved enough to change the value substantially, then
		//	we update `this` which is the input.  We make sure the change is at least
		//	sliderBinSize because, setting the input triggers the slider to move 
		//	which then rounds off to the nearest sliderBinSize and calls this.
		_afterSliderChange : function(e) {
			//Y.log('in _afterSliderChange');
			var oldValue  = parseFloat(this.get("value"));
			var nv = this.valueMin + ((e.newVal - this.sliderMin)/this.slider2InputDenom);
			//Y.log('this._afterSliderChange with e.newVal=' + e.newVal + '	 oldValue=' + oldValue + '	nv='+nv);
			if (Math.abs(oldValue - nv) > this.sliderBinSize/2) {
				if (nv <= this.valueMax && nv >= this.valueMin) {
					this.inputNode.setStyle('color', 'black');
				}
				this.set("value", nv );
			}
		},

		// updates the input box when the value changes
		_afterValueChange : function(e) {
			//Y.log('in _afterValueChange');
			this._uiSetValue(e.newVal);
		},

		// Updates the input box and slider to reflect val
		_uiSetValue : function(val) {
			//Y.log('in _uiSetValue(' + val + ')');
			var nodeV = this.inputNode.get("value");
			if (Math.abs(+val - +nodeV) > 1e-9) {
				this.inputNode.set("value", val.toFixed(9).replace(/0+$/, '0'));
			}
			else {
				//Y.log('prev was ' + nodeV + ' not changing');
				
			}
			var sliderValue = this.sliderMin + this.slider2InputDenom*(val - this.valueMin);
			if (this.slider.wait) {
				this.slider.wait.cancel();
			}
				// Update the Slider on a delay to allow time for typing
			this.slider.wait = Y.later( 20, this.slider, function () {
				this.wait = null;
				this.set( "value", sliderValue );
			});
		},

		// returns true if the value is valid
		_validateValue: function(val) {
			var min = this.get("min");
			var max = this.get("max");
			var n = (Y.Lang.isNumber(+val));
			var low = +val >= +min;
			var high =  +val <= +max;
			var b = n && low && high;
			//Y.log('_validateValue(' + val + ') returning ' + b + '(' + n + ', ' + low + ', ' + high + ')');
			return b;
	  }
	});

/*	Y.log('about to loop over suffixes');

	var suffixArray = ['a', 'b', 'c', 'd', 'internal'];
	for (var i = 0; i < suffixArray.length; ++i) {
		var suffix = suffixArray[i];
		try {
			createSliderForInput({
				valueMax : 0.5,
				inputSelector :	 "#horiz_value_" +	suffix,
				sliderSelector : '#horiz_slider_' + suffix,
			});
			
		}
		catch (e) {
			Y.log("Exception in createSliderForInput: " + e);
			throw e;
		}
	}	
*/
//Y.log("creating DualInputSlider");
	try {
		var spinner = new DualInputSlider({
			srcNode: "#numberField",
			max : 0.5,
			min : 0.0,
			minorStep : 0.0001,
			majorStep : 0.01,
		});
		spinner.render();
		spinner.focus();
	}
	catch (e) {
		logException(e, Y.log);
		try {
			logException(e, Y.log);
		}
		catch (ee) {
			Y.log("EE = " + ee);
		}
		throw e;
	}
	
	return;
}
);

