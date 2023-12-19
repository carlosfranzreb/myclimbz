function sortOrNavigate(col, dir) {
  var table = document.getElementById("routes_table");
  var rowCount = table.rows.length - 1; // Exclude header row if applicable

  if (rowCount < 500) {
      // Call the sorting function if the table has less than 500 entries
      sortTable(table, col, dir);
  } else {
      // Redirect to the specified URL if the table has 500 or more entries
      window.location.href = "/routes?sort=" + encodeURIComponent(col) + "&dir=" + encodeURIComponent(dir);
  }
}




function sortTable(table, col, dir) {
    var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    switching = true;
    // Set the sorting direction to ascending:
    dir = 1;
    /* Make a loop that will continue until
    no switching has been done: */
    while (switching) {
      // Start by saying: no switching is done:
      switching = false;
      rows = table.rows;
      /* Loop through all table rows (except the
      first, which contains table headers): */
      for (i = 1; i < (rows.length - 1); i++) {
        // Start by saying there should be no switching:
        shouldSwitch = false;
        /* Get the two elements you want to compare,
        one from current row and one from the next: */
        x = rows[i].getElementsByTagName("TD")[col];
        y = rows[i + 1].getElementsByTagName("TD")[col];
        /* Check if the two rows should switch place,
        based on the direction, asc or desc: */
        if (dir == 1) {
          if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        } else if (dir == -1) {
          if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
            // If so, mark as a switch and break the loop:
            shouldSwitch = true;
            break;
          }
        }
      }
      if (shouldSwitch) {
        /* If a switch has been marked, make the switch
        and mark that a switch has been done: */
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        switching = true;
        // Each time a switch is done, increase this count by 1:
        switchcount ++;
      } else {
        /* If no switching has been done AND the direction is "asc",
        set the direction to -1 and run the while loop again. */
        if (switchcount == 0 && dir == "asc") {
          dir = -1;
          switching = true;
        }
      }
    }
  }