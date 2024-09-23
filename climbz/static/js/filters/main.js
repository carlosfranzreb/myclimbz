class Grade {
	constructor(grade) {
		this.grade_dict = GRADES.find((obj) => obj[GRADE_SCALE] === grade);
		this.scale = GRADE_SCALE;
	}

	valueOf() {
		if (this.grade_dict === undefined) return NaN;
		return this.grade_dict.level;
	}
}

let FILTER_WIDGETS = [];

// --- List of available filters and their corresponding functions
FILTERS = {
	Grade: {
		filter_type: "slider",
		data_class: Grade,
		step: 1,
		data_column: "level",
		row: 0,
		col: 0,
	},
	Date: {
		filter_type: "date_range",
		data_class: Date,
		data_column: "dates",
		row: 3,
		col: 0,
	},
	Inclination: {
		filter_type: "slider",
		data_class: Number,
		step: 5,
		data_column: "inclination",
		row: 1,
		col: 0,
	},
	Landing: {
		filter_type: "slider",
		data_class: Number,
		step: 1,
		data_column: "landing",
		row: 0,
		col: 1,
	},
	Attempts: {
		filter_type: "slider",
		data_class: Number,
		step: 1,
		data_column: "n_attempts_send",
		row: 2,
		col: 0,
	},
	Height: {
		filter_type: "slider",
		data_class: Number,
		step: 0.5,
		data_column: "height",
		row: 1,
		col: 1,
	},
	Area: {
		filter_type: "dropdown",
		data_column: "area",
		row: 2,
		col: 1,
	},
	Crux: {
		filter_type: "dropdown",
		data_column: "cruxes",
		row: 2,
		col: 1,
	},
	Sends: {
		filter_type: "radio",
		data_column: "sent",
		options: ["All", "Projects", "Sent"],
		truth_values: [[true, false], false, true],
		row: 3,
		col: 1,
	},
};

// Filter the global data according to the active filters
function filter_data() {
	// Remove unsent climbs if the corresponding button is unchecked
	let this_data = null;
	this_data = DATA;
	if (FILTER_WIDGETS.length === 0) return this_data;

	// Apply the active filters
	let filtered_data = [];
	for (let climb of this_data) {
		let include = false;
		for (let w of FILTER_WIDGETS) {
			include = w.filter_value(climb[w.data_column]);
			if (!include) break;
		}
		if (include) filtered_data.push(climb);
	}
	return filtered_data;
}
