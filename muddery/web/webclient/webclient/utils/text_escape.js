
if (typeof(require) != "undefined") {
    require("../client/defines.js");
}

TextEscape = function() {
	// Compile RegExps.
	this.regexp_escape.compile(this.regexp_escape);
}

TextEscape.prototype = {
    regexp_escape : /\$[0-9|_|A-Z]+|\$\$/g,

    parse: function(string, values) {
        var converter = function(match) {
            if (match == "$$") {
                return "$";
            }
            else if (match in values) {
                return values[match];
            }
            else {
                return match;
            }
        };

        // Parses a string, replace escapes with values
        string = string.replace(this.regexp_escape, converter);
        return string;
    },
};



