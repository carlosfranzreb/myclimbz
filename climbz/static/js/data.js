// Logic and variables that are common to both tables and plots

// Global variables shared by tables and plots
let DATA = null;
let GRADES = null;
let DISPLAYED_DATA = null;
let DISPLAY_FORM = "table"; // Table or plot

let GRADE_SCALE = "font"; // Scale chosen with the toggle button

let font_grades_list = null;
let hueco_grades_list = null;

let font_grades_regex = null;
let hueco_grades_regex = null;

CRUXES = [
  "Crimp",
  "Sloper",
  "Pocket",
  "Tension",
  "Compression",
  "Heel hook",
  "Toe hook",
  "Undercling",
  "Shoulder",
  "Wrist",
  "Drag",
  "Power",
  "Lock-off",
  "Top out",
  "Feet",
  "Mantel",
];

// Add an event listener to the checkbox "display-form-toggle"
let display_form_toggle = document.getElementById("display-form-toggle");
display_form_toggle.addEventListener("change", function () {
  DISPLAY_FORM = display_form_toggle.checked ? "plot" : "table";
  display_data();
});

function start_display(data, grades, session_date) {
  DATA = data;
  GRADES = grades;

  font_grades_list = GRADES.map((obj) => obj["font"]);
  hueco_grades_list = GRADES.map((obj) => obj["hueco"]);

  font_grades_regex = new RegExp(font_grades_list.join("|"), "i");
  hueco_grades_regex = new RegExp(hueco_grades_list.join("|"), "i");

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
    document.getElementById("y-axis-select").options.add(new Option(key, key));
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

  // hide/show plot-axes
  let plot_axes = document.getElementById("plot-axes");
  plot_axes.style.display = DISPLAY_FORM == "plot" ? "block" : "none";

  // Display the data
  if (DISPLAY_FORM == "table") show_table();
  else show_plot();
}

function create_filter(id) {
  window.filter_button = new FilterWidget(id, 50);
}

let CSV_IMPORT_OPTIONS = {
  name: "Name",
  level: "Grade",
  level_felt: "Grade felt",
  area: "Area",
  sector: "Sector",
  height: "Height",
  inclination: "Inclination",
  landing: "Landing",
  sent: "Sent",
  conditions: "Conditions",
  cruxes: "Cruxes",
  n_attempts_all: "No. of attempts",
  n_attempts_send: "No. of attempts to send",
  n_sessions: "No. of sessions", //? Necessary?
  dates: "Dates",
};
let OBLIGATORY_OPTS = ["name", "area"];

function check_option_validity(name, selected_index, select) {
  let is_valid = true;
  let selected_option = select.options[selected_index].value;
  if (name === "Grade" || name === "Grade felt") {
    //check that all the values in the column of csv_data are valid grades
    for (let row of csv_data) {
      if (
        row[selected_option] !== "" &&
        !font_grades_regex.test(row[selected_option]) &&
        !hueco_grades_regex.test(row[selected_option])
      ) {
        alert("The column " + selected_option + " contains invalid grades.");
        return false;
      }
    }
  } else if (
    name === "No. of attempts" ||
    name === "No. of attempts to send" ||
    name === "No. of sessions" ||
    name === "Height" ||
    name === "Inclination"
  ) {
    //check that all the values in the column of csv_data are numbers
    for (let row of csv_data) {
      if (isNaN(row[selected_option])) {
        alert(
          "The column " + selected_option + " contains non-numeric values."
        );
        return false;
      }
    }
  } else if (name === "Name" || name === "Area" || name === "Sector") {
    //check that all the values in the column of csv_data are less than 200 characters
    for (let row of csv_data) {
      if (row[selected_option].length > 200) {
        alert(
          "The column " +
            selected_option +
            " contains values longer than 200 characters."
        );
        return false;
      }
    }
  } else if (name === "Conditions" || name === "Landing") {
    //check that all the values in the column of csv_data are numbers between 0 and 10
    for (let row of csv_data) {
      if (
        isNaN(row[selected_option]) ||
        row[selected_option] < 1 ||
        row[selected_option] > 10
      ) {
        alert(
          "The column " +
            selected_option +
            " contains values outside the range 1-10."
        );
        return false;
      }
    }
  } else if (name === "Sent") {
    //check that all the values in the column of csv_data are "yes"/"true" or "no"/"false"/empty, if not true or false change to true or false
    for (let row of csv_data) {
      if (
        row[selected_option] !== "yes" &&
        row[selected_option] !== "true" &&
        row[selected_option] !== "no" &&
        row[selected_option] !== "false" &&
        row[selected_option] !== ""
      ) {
        alert(
          "For the Sent column only the values 'yes', 'true', 'no', 'false' or empty are allowed."
        );
        return false;
      }
    }
  } else if (name === "Dates") {
    //check that all the values in the column of csv_data are valid dates
    let parseTime = d3.timeParse("%d/%m/%Y");
    for (let row of csv_data) {
      if (
        row[selected_option] !== "" &&
        parseTime(row[selected_option]) === null
      ) {
        alert(
          "The column " +
            selected_option +
            " contains invalid dates. The dates should be in the format 'dd/mm/yyyy' or empty."
        );
        return false;
      }
    }
  }
  //check if the column is obligatory and if it contains empty rows, use CSV_IMPORT_OPTIONS to get the name of the column
  if (OBLIGATORY_OPTS.some((s) => CSV_IMPORT_OPTIONS[s] === name)) {
    for (let row of csv_data) {
      if (row[selected_option] === "") {
        alert("The column " + selected_option + " contains empty rows.");
        return false;
      }
    }
  }
  return is_valid;
}

function add_data_columns_csv(id) {
  let dialog_body = document.getElementById(id);
  let selected_indices = {};
  for (let key in CSV_IMPORT_OPTIONS) {
    let div = document.createElement("div");
    div.className = "row";
    div.style.margin = "10px";

    let col1 = document.createElement("div");
    col1.className = "col";

    let label = document.createElement("label");
    label.htmlFor = "csv_select_" + key;
    label.textContent = CSV_IMPORT_OPTIONS[key];
    col1.appendChild(label);
    div.appendChild(col1);

    let col2 = document.createElement("div");
    col2.className = "col";

    let select = document.createElement("select");
    select.className = "form-control";
    select.id = "csv_select_" + key;

    // Add a default option with the key as the placeholder
    let defaultOption = document.createElement("option");
    //defaultOption.id = "csv_default_option";
    defaultOption.value = "";
    defaultOption.textContent = "--";
    select.appendChild(defaultOption);

    selected_indices[select.id] = 0;

    col2.appendChild(select);
    div.appendChild(col2);

    function disableSelectedOption(selectedIndex, prev_index, select_id) {
      for (let key in CSV_IMPORT_OPTIONS) {
        let select = document.getElementById("csv_select_" + key);
        if (select.id !== select_id) {
          select.options[prev_index].disabled = false;
          if (selectedIndex !== 0) {
            select.options[selectedIndex].disabled = true;
          }
        }
      }
    }

    select.addEventListener("change", function () {
      let is_valid = true;
      if (select.selectedIndex !== 0 && csv_data !== null) {
        //get the text in the label of the selected select
        let select_label = document.querySelector(
          'label[for="' + select.id + '"]'
        ).textContent;
        is_valid = check_option_validity(
          select_label,
          select.selectedIndex,
          select
        );
      }
      if (is_valid) {
        disableSelectedOption(
          select.selectedIndex,
          selected_indices[select.id],
          select.id
        );
      } else {
        // Reset the select to the previous index
        select.selectedIndex = selected_indices[select.id];
        return;
      }
      selected_indices[select.id] = select.selectedIndex;
    });

    dialog_body.appendChild(div);
  }
}

let csv_file_form = document.getElementById("csv_file_form");
let csv_data = null;

function parse(file) {
  // Always return a Promise
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    let data;
    reader.onloadend = function (e) {
      data = d3.csvParse(e.target.result);
      resolve(data);
    };
    // Make sure to handle error states
    reader.onerror = function (e) {
      reject(e);
    };
    reader.readAsText(file);
  });
}

async function import_csv() {
  if (csv_file_form.files.length === 0) {
    alert("No file selected.");
    return;
  }
  let csv_file_type = csv_file_form.files[0].type;
  if (csv_file_type !== "text/csv") {
    alert("The file must be a CSV file.");
    csv_file_form.value = null;
    return;
  }
  csv_data = await parse(csv_file_form.files[0]);
  let cols = csv_data.columns;

  //add options to select columns
  let preselected_cols = {};
  for (let key in CSV_IMPORT_OPTIONS) {
    let select = document.getElementById("csv_select_" + key);
    for (let col of cols) {
      let option = document.createElement("option");
      option.value = col;
      option.textContent = col;
      select.appendChild(option);
      //if the col is the same as the options value, set it as the selected option
      if (col.toLowerCase() === CSV_IMPORT_OPTIONS[key].toLowerCase()) {
        preselected_cols[key] = col;
      }
    }
  }
  for (let key in preselected_cols) {
    let select = document.getElementById("csv_select_" + key);
    select.value = preselected_cols[key];
    //send change event to the select to disable the selected option in the other selects
    let event = new Event("change");
    select.dispatchEvent(event);
  }
}

function remove_csv_options() {
  //remove the options from the select columns except the default option
  for (let key in CSV_IMPORT_OPTIONS) {
    let select = document.getElementById("csv_select_" + key);
    for (let i = select.options.length - 1; i > 0; i--) {
      select.remove(i);
    }
  }
}

//TODO: what about slash grades?
//TODO: improve cruxes list: bunchy, hard start, sidepull, rockover, edge, pinch

csv_file_form.addEventListener("change", import_csv);
document
  .getElementById("cancel_csv_button")
  .addEventListener("click", function (e) {
    csv_file_form.value = null;
    csv_data = null;
    remove_csv_options();
  });
document
  .getElementById("csv_dialog_close_button")
  .addEventListener("click", function (e) {
    csv_file_form.value = null;
    csv_data = null;
    remove_csv_options();
  });
document
  .getElementById("confirm_csv_import_button")
  .addEventListener("click", function (e) {
    if (
      csv_data === null ||
      csv_file_form.value === null ||
      csv_file_form.files.length === 0
    ) {
      alert("No file selected.");
      return;
    }
    //check that the csv_data is not full of empty rows
    if (
      csv_data.length === 0 ||
      csv_data.every((row) => {
        if (Object.keys(row).length === 0) {
          return true;
        }
        return false;
      })
    ) {
      alert("The file is empty.");
      return;
    }
    let options_map = {};
    for (let key in CSV_IMPORT_OPTIONS) {
      let select = document.getElementById("csv_select_" + key);
      let selected_index = select.selectedIndex;
      if (selected_index !== 0) {
        let selected_option = select.options[selected_index].value;
        options_map[key] = selected_option;
      }
    }
    let sent_col = options_map["sent"] || null;
    if (sent_col in csv_data[0]) {
      //Change the values of sent to true or false
      csv_data.forEach((row) => {
        if (
          row[sent_col] === "yes" ||
          row[sent_col] === "true" ||
          row[sent_col] === true
        ) {
          row[sent_col] = true;
        } else {
          row[sent_col] = false;
        }
      });
    }
    //add the csv_data to the database
    if (!check_csv_import(csv_data, options_map)) {
      return;
    }

    //change the csv_data to the selected columns inplace of the original columns
    let unused_cols = csv_data.columns.slice();
    for (let key in CSV_IMPORT_OPTIONS) {
      if (key in options_map) {
        unused_cols = unused_cols.filter((col) => col !== options_map[key]);
        csv_data.forEach((row) => {
          row[key] = row[options_map[key]];
          delete row[options_map[key]];
        });
      }
    }
    //delete the unused columns
    for (let col of unused_cols) {
      csv_data.forEach((row) => delete row[col]);
    }
    if ("cruxes" in csv_data[0]) {
      //Change the values of cruxes to an array
      csv_data.forEach((row) => {
        row["cruxes"] = row["cruxes"].split(" ");
      });
      //For each crux in the cruxes array, check the stringSimilarity with the cruxes in the database
      csv_data.forEach((row) => {
        row["cruxes"] = row["cruxes"].map((crux) => {
          for (let db_crux of CRUXES) {
            let similarity = stringSimilarity(crux, db_crux);
            if (similarity > 0.5) {
              return db_crux;
            }
          }
          //if nothing is similar delete the crux
          return null;
        });
        row["cruxes"] = row["cruxes"].filter((crux) => crux !== null);
      });
    }
    console.log(csv_data);
    let data = JSON.stringify(csv_data);
    let form = new FormData();
    form.append("csv_data", data);
    form.append("data_type", "csv");
    form.append(
      "csrf_token",
      document.querySelector('input[name="csrf_token"]').value
    );

    fetch("/", {
      method: "POST",
      body: form,
    }).then((response) => {
      if (response.ok) {
        window.location.reload();
      } else {
        alert("An error occurred while importing the data.");
      }
    });
    csv_data = null;
    csv_file_form.value = null;
    remove_csv_options();
    let myModalEl = document.getElementById("import_csv_dialog");
    let modal = bootstrap.Modal.getInstance(myModalEl);
    modal.hide();
  });

var check_csv_import = function (csv_data, options_map) {
  //check that if the "sent" column has true, there is a "dates" column, and if a row has "sent" as true, it has a date
  let sent_col = options_map["sent"] || null;
  let dates_col = options_map["dates"] || null;
  if (sent_col in csv_data[0]) {
    let any_sent = csv_data.some((row) => row[sent_col] === true);
    if (any_sent) {
      if (!(dates_col in csv_data[0])) {
        alert("There are sent boulders, but no dates column.");
        return false;
      }
      let any_no_date = csv_data.some(
        (row) => row[sent_col] === true && row[dates_col] === ""
      );
      if (any_no_date) {
        alert("There are sent boulders without a corresponding date.");
        return false;
      }
    }
  }
  //check that all the obligatory columns are present
  for (let col of OBLIGATORY_OPTS) {
    if (!csv_data[0].hasOwnProperty(options_map[col])) {
      alert("The column " + CSV_IMPORT_OPTIONS[col] + " is missing.");
      return false;
    }
  }

  return true;
};

var stringSimilarity = function (str1, str2, substringLength, caseSensitive) {
  if (substringLength === void 0) {
    substringLength = 2;
  }
  if (caseSensitive === void 0) {
    caseSensitive = false;
  }
  if (!caseSensitive) {
    str1 = str1.toLowerCase();
    str2 = str2.toLowerCase();
  }
  if (str1.length < substringLength || str2.length < substringLength) return 0;
  let map = new Map();
  for (let i = 0; i < str1.length - (substringLength - 1); i++) {
    let substr1 = str1.substr(i, substringLength);
    map.set(substr1, map.has(substr1) ? map.get(substr1) + 1 : 1);
  }
  let match = 0;
  for (var j = 0; j < str2.length - (substringLength - 1); j++) {
    let substr2 = str2.substr(j, substringLength);
    let count = map.has(substr2) ? map.get(substr2) : 0;
    if (count > 0) {
      map.set(substr2, count - 1);
      match++;
    }
  }
  return (match * 2) / (str1.length + str2.length - (substringLength - 1) * 2);
};
