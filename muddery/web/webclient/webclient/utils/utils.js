
MudderyUtils = function() {
}

MudderyUtils.prototype = {

    visual_length: function(str) {
        var length = 0;
        for (var i = 0; i < str.length; i++) {
            var c = str.charCodeAt(i);
            if ((c >= 0x0001 && c <= 0x007e) || (0xff60 <= c && c <= 0xff9f)) {
                // single length
                length += 1;
            }
            else {
                // double length
                length += 2;
            }
        }
        return length;
    },

    truncate_string: function(str, max_length, add_points) {
        // Trunc the string to specified length.
        // args:
        //      str - origin string
        //      max_length - the max visual length.
        //                   For example, the length of English characters is 1,
        //                   while Chinese characters is 2.
        //      add_points - add 2 points to the end of the string or not

        var total = 0;
        var c = 0;
        for (var i = 0; i < str.length; i++) {
            c = str.charCodeAt(i);
            if ((c >= 0x0001 && c <= 0x007e) || (0xff60 <= c && c <= 0xff9f)) {
                // single length
                total += 1;
            }
            else {
                // double length
                total += 2;
            }
            
            if (total > max_length) {
                var last = 0;
                if (!add_points) {
                    last = i - 1;
                }
                else {
                    // get place of points
                    last = i;
                    while (last > 0) {
                        c = str.charCodeAt(last);
                        if ((c >= 0x0001 && c <= 0x007e) || (0xff60 <= c && c <= 0xff9f)) {
                            // single length
                            total -= 1;
                        }
                        else {
                            // double length
                            total -= 2;
                        }
                        --last;
                        
                        if (total <= max_length - 2) {
                            break;
                        }
                    }
                }
                
                if (last < 0) {
                    last = 0;
                }

                str = str.substring(0, last + 1)

                if (add_points) {
                    str += '..';
                }
                
                break;
            }
        }
        
        return str;
    },

    time_to_string: function(time) {
        if (time < 0) {
            return "--";
        }

        var minutes = parseInt(time / 60);
        var seconds = (time - minutes * 60).toFixed(0);
        if (seconds < 10) {
            seconds = "0" + seconds;
        }
        return minutes + ":" + seconds;
    },
};


/***************************************
 *
 * Store game data.
 *
 ***************************************/
MudderyDataHandler = function() {
}

MudderyDataHandler.prototype = {
    character_dbref: "",
    character_name: "",
    character_level: 0,
    current_target: "",
    name_list: {},
    dialogues_list: [],
    skill_cd_time: {},

    getEscapes: function() {
        return {"$PLAYER_NAME": this.character_name};
    },

    setSkills: function(skills) {
        var current_time = (new Date()).valueOf();

        for (var i in skills) {
            var key = skills[i]["key"];

            // cd_time in milliseconds
            var cd_time = current_time + skills[i]["cd_remain"] * 1000;
            this.skill_cd_time[key] = cd_time;
        }
    },

    setSkillCD: function(skill, cd, gcd) {
        // update skill's cd
        var current_time = (new Date()).valueOf();

        // cd_time in milliseconds
        var cd_time = current_time + cd * 1000;
        if (skill in this.skill_cd_time) {
            if (this.skill_cd_time[skill] < cd_time) {
                this.skill_cd_time[skill] = cd_time;
            }
        }
        else {
            this.skill_cd_time[skill] = cd_time;
        }

        var gcd_time = current_time + gcd * 1000;
        for (var key in this.skill_cd_time) {
            if (this.skill_cd_time[key] < gcd_time) {
                this.skill_cd_time[key] = gcd_time;
            }
        }
    },
};


/***************************************
 *
 * Parse text marks to html marks.
 *
 ***************************************/
MudderyText2HTML = function() {
	// Compile RegExps.
	this.regexp_html.compile(this.regexp_html);

	var mark_pattern = new Array();
	for (mark in this.mark_map) {
		mark = mark.replace(/\[/, "\\[");
		mark = mark.replace(/\*/, "\\*");
		mark_pattern.push(mark);
	}
	mark_pattern = mark_pattern.join("|");
	mark_pattern = new RegExp(mark_pattern, "g");
	this.regexp_mark.compile(mark_pattern);
}

MudderyText2HTML.prototype = {
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

    parseHtml: function(string) {
        // Parses a string, replace markup with html
        var org_string = string;
        try {
			// Convert html codes.
			string = string.replace(this.regexp_html, this.convertHtml);

			// Convert marks
			var last_convert = "";
			string = string.replace(this.regexp_mark, function(match) {
                var replacement = "";

                // <span> can contain <string>
                if (last_convert.substring(0, 5) == "<span" && match != "{h") {
                    // close span
                    replacement = "</span>";
                }
                else if (last_convert.substring(0, 8) == "<strong>" && match != "{H") {
                    // close strong
                    replacement = "</strong>";
                }

                if (match in core.text2html.mark_map) {
                    last_convert = core.text2html.mark_map[match];
                    replacement += last_convert;
                }

                return replacement;}
            );

			if (last_convert.substring(0, 5) == "<span") {
				// close span
				string += "</span>";
			}
			else if (last_convert.substring(0, 8) == "<strong>") {
				// close strong
				string += "</strong>";
			}
		}
		catch(error) {
            console.error(error.message);
            string = org_string;
        }

        return string;
    },

    clearTag: function(match) {
        var replacement = "";

        if (match in this.mark_map) {
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
        string = string.replace(this.regexp_mark, this.clearTag);
        return string;
    }
}


/***************************************
 *
 * Parse text marks with local data.
 *
 ***************************************/
MudderyTextEscape = function() {
	// Compile RegExps.
	this.regexp_escape.compile(this.regexp_escape);
}

MudderyTextEscape.prototype = {
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


/***************************************
 *
 * Translate strings to local languages.
 *
 ***************************************/
MudderyLocalString = function() {
}

MudderyLocalString.prototype = {
	string_dict: MudderyLocalString,

	translate: function(str) {
		if (str in this.string_dict) {
        	return this.string_dict[str];
    	}

    	return str;
	},
}
