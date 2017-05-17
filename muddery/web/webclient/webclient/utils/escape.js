
var escape = {
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
        string = string.replace(escape.regexp_escape, converter);
        return string;
    },
};

// Compile RegExps.
escape.regexp_escape.compile(escape.regexp_escape);


