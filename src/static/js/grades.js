/* Utility functions regarding grades */


// Return false if b is larger than a, true otherwise
function compareMapGrades(a, b) {
    a = a[0];
    b = b[0];
    // If both numbers are the same, go to letter
    if (a[0] == b[0]) { 
        // If one of the grades doesn't have a letter
        if (a.length == 1 || b.length == 1)
            return a.length >= b.length ? 1 : -1;
        // If both grades have the same letter, check for "+"
        if (a[1] == b[1])
            return a.length >= b.length ? 1 : -1;
        // If both grades have different letters, compare them
        else
            return a[1] > b[1] ? 1 : -1;
    }
    // If both numbers are different, compare them
    else
        return a[0] > b[0] ? 1 : -1;
}