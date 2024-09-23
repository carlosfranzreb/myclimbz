// Logic and variables that are common to both tables and plots

// Global variables shared by tables and plots
let DATA = null;
let GRADES = null;
let DISPLAYED_DATA = null;
let DISPLAY_FORM = "table"; // Table or plot

let font_grades_list = null;
let hueco_grades_list = null;

// Add an event listener to the button "display-form-toggle"
let display_form_toggle = document.getElementById("display-form-toggle");
if (display_form_toggle)
	display_form_toggle.addEventListener("click", function () {
		let btn_value = display_form_toggle.innerHTML.toLowerCase();
		display_form_toggle.innerHTML = btn_value == "table" ? "Plot" : "Table";
		DISPLAY_FORM = btn_value.toLowerCase();
		display_data();
	});

function start_display(data, grades, session_date) {
	DATA = data;
	GRADES = grades;

	font_grades_list = GRADES.map((obj) => obj["font"]);
	hueco_grades_list = GRADES.map((obj) => obj["hueco"]);

	// Parse the dates and format them to "dd/mm/yyyy"
	let parseTime = d3.timeParse("%a, %d %b %Y %H:%M:%S");
	let formatDate = d3.timeFormat("%d/%m/%Y");
	DATA = DATA.map((d) => {
		if (d.dates.length == 0) {
			d.dates = [""];
			d.last_climbed = "";
			return d;
		}
		let parsed_dates = d.dates.map((date) =>
			parseTime(date.substring(0, date.length - 4))
		);
		d.dates = parsed_dates.map((date) => formatDate(date));
		let max_date = Math.max(...parsed_dates);
		d.last_climbed = formatDate(max_date);
		return d;
	});

	// Set the options of the plot axes
	for (let key of Object.keys(y_axis_options))
		document
			.getElementById("y-axis-select")
			.options.add(new Option(key, key));
	for (let [key, value] of Object.entries(x_axis_options)) {
		document
			.getElementById("x-axis-select")
			.options.add(new Option(value, key));
	}
	document.getElementById("x-axis-select").value = "level";

	display_data();
}

function display_data() {
	// Filter the data according to the active filters
	DISPLAYED_DATA = filter_data();

	// Remove the previous table or plot
	d3.select("#content_div").selectAll("*").remove();
	window.data_table = null;

	// hide/show plot-axes
	let plot_axes = document.getElementById("plot-axes");
	plot_axes.style.display = DISPLAY_FORM == "plot" ? "block" : "none";

	// Display the data
	if (DISPLAY_FORM == "table") {
		show_table();
		hide_columns();
	} else {
		show_plot();
	}
}

function create_filter(id) {
	window.filter_button = new FilterWidget(id, 50);
}
