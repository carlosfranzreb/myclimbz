/*
 * Defines the Grade class.
 */

class Grade {
    constructor(grade) {
        this.scale = GRADE_SCALE;
        this.grade_dict = GRADES.find(obj => obj[this.scale] === grade);
    }
    
    get get_grade() {
        return this.grade_dict[this.scale];
    }

    set set_grade(grade) {

        // Check that the value is valid
        let grade_dict = GRADES.find(obj => obj[this.scale] === grade);
        if (grade_dict == undefined)
            throw new Error("Grade not found: " + grade);
        else
            this.grade_dict = grade_dict;
    }

    get get_level() {
        return this.grade_dict.level;
    }

    get get_scale() {
        return this.scale;
    }

    set set_scale(scale) {

        // Check that the value is valid and set it if it is
        if (scale != "font" && scale != "hueco")
            throw new Error("Invalid grade scale: " + scale);
        this.scale = scale;
    }
}

Grade.prototype.toString = function() {
    return this.grade_dict[this.scale];
}

Grade.prototype.valueOf = function() {
    return this.grade_dict.level;
}