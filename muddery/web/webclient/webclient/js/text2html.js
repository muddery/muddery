
var text2html = {
    mark_map : {
        '{{' : '{',                  // "{"
        '{n' : '',                   // reset            Close the span.
        '{/' : '<br>',               // line break
        '{-' : '    ',               // tab
        '{_' : '&#8199;',            // space

        // Replace ansi colors with html color class names.
        // Let the client choose how it will display colors, if it wishes to.
        '{r' : '<span class="red">',
        '{g' : '<span class="lime">',
        '{y' : '<span class="yellow">',
        '{b' : '<span class="blue">',
        '{m' : '<span class="magenta">',
        '{c' : '<span class="cyan">',
        '{w' : '<span class="white">',
        '{x' : '<span class="dimgray">',     // dark grey
                     
        '{R' : '<span class="maroon">',
        '{G' : '<span class="green">',
        '{Y' : '<span class="olive">',
        '{B' : '<span class="navy">',
        '{M' : '<span class="purple">',
        '{C' : '<span class="teal">',
        '{W' : '<span class="gray">',        // light grey
        '{X' : '<span class="black">',       // pure black
                        
        // hilight-able colors
        '{h' : '<strong>',                   // begin hilight
        '{H' : '</strong>',                  // finish hilight

        // backgrounds
        '{[r' : '<span class="bgred">',
        '{[g' : '<span class="bglime">',
        '{[y' : '<span class="bgyellow">',
        '{[b' : '<span class="bgblue">',
        '{[m' : '<span class="bgmagenta">',
        '{[c' : '<span class="bgcyan">',
        '{[w' : '<span class="bgwhite">',   // white background
        '{[x' : '<span class="bgdimgray">', // dark grey background

        '{[R' : '<span class="bgmaroon">',
        '{[G' : '<span class="bggreen">',
        '{[Y' : '<span class="bgolive">',
        '{[B' : '<span class="bgnavy">',
        '{[M' : '<span class="bgpurple">',
        '{[C' : '<span class="bgteal">',
        '{[W' : '<span class="bggray">',     // light grey background
        '{[X' : '<span class="bgblack">',    // pure black background
                       
        '{lc' : '<a href="#" onclick="doSendText(\'',    	// link
        '{lt' : '\')">',                                    // link
        '{le' : '</a>',                                     // link
    },

    regexp_html : /"|&|'|<|>|  |\x0A/g,

    regexp_mark : /\w*/,

    last_convert : "",
    
    convertHtml: function(match) {
        if (match == "  ") {
            return "&#8199;&#8199;";
        }
        else {
            var char = match.charCodeAt(0);
            if (char == 0x0A) {
                return "<br>";
            }
            else {
                var replacement = ["&#"];
                replacement.push(char);
                replacement.push(";");
                return replacement.join("");
            }
        }
    },

    convertMark: function(match) {
        var replacement = "";
        
        // <span> can contain <string>
        if (text2html.last_convert.substring(0, 5) == "<span" && match != "{h") {
            // close span
            replacement = "</span>";
        }
        else if (text2html.last_convert.substring(0, 8) == "<strong>" && match != "{H") {
            // close strong
            replacement = "</strong>";
        }
        
        if (match in text2html.mark_map) {
            text2html.last_convert = text2html.mark_map[match];
            replacement += text2html.last_convert;
        }
        
        return replacement;
    },

    parseHtml: function(string) {
        // Parses a string, replace markup with html
        var org_string = string;
        try {
			// Convert html codes.
			string = string.replace(text2html.regexp_html, text2html.convertHtml);

			// Convert marks
			string = string.replace(text2html.regexp_mark, text2html.convertMark);

			if (text2html.last_convert.substring(0, 5) == "<span") {
				// close span
				string += "</span>";
			}
			else if (text2html.last_convert.substring(0, 8) == "<strong>") {
				// close strong
				string += "</strong>";
			}

			// Clear last convert.
			text2html.last_convert = "";
		}
		catch(error) {
            console.error(error.message);
            string = org_string;
        }
        
        return string;
    },

    clearTag: function(match) {
        var replacement = "";

        if (match in text2html.mark_map) {
            if (match == "{{") {
                // "{"
                replacement = "{";
            }
            else if (match == "{/") {
                // line break
                replacement = " ";
            }
            else if (match == "{-") {
                // tab
                replacement = "    ";
            }
            else if (match == "{_") {
                // space
                replacement = " ";
            }
            else {
                replacement = "";
            }
        }
        else {
            replacement = match;
        }

        return replacement;
    },

    clearTags: function(string) {
        string = string.replace(text2html.regexp_mark, text2html.clearTag);
        return string;
    }
};

// Compile RegExps.
text2html.regexp_html.compile(text2html.regexp_html);

var mark_pattern = new Array();
for (mark in text2html.mark_map) {
    mark = mark.replace(/\[/, "\\[");
    mark = mark.replace(/\*/, "\\*");
    mark_pattern.push(mark);
}
mark_pattern = mark_pattern.join("|");
mark_pattern = new RegExp(mark_pattern, "g");
text2html.regexp_mark.compile(mark_pattern);

