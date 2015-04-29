
var text2html = {
    MARK_MAP : {
        '{{' : '{',                  // "{"
        '{n' : '',                   // reset            Close the span.
        '{/' : '<br>',               // line break
        '{-' : '    ',               // tab
        '{_' : '&nbsp;',             // space
        '{*' : '',                   // invert           Does not support it, remove it only.
        '{^' : '',                   // blinking text    Does not support it, remove it only.

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
                       
        '{lc' : '<a href="#" onclick="websocket.send(\'CMD ',    // link
        '{lt' : '\'); return false;">',                          // link
        '{le' : '</a>',                                         // link

    //        xterm256_map = [
    //        '\{[0-5]{3}', ""),   # {123 - foreground colour
    //        '\{\[[0-5]{3}', "")   # {[123 - background colour
    },

    REGEXP_HTML : /"|&|'|<|>|  |\x0A/g,

    REGEXP_MARK : /\w*/,

    LAST_CONVERT : "",
    
    convert_html: function(match){
        if (match == "  "){
            return "&#8199;&#8199;";
        }
        else{
            var char = match.charCodeAt(0);
            if (char == 0x0A){
                return "<br>";
            }
            else{
                var replacement = ["&#"];
                replacement.push(char);
                replacement.push(";");
                return replacement.join("");
            }
        }
    },

    convert_mark: function(match){
        var replacement = "";
        
        // <span> can contain <string>
        if (text2html.LAST_CONVERT.substring(0, 5) == "<span" && match != "{h"){
            // close span
            replacement = "</span>";
        }
        else if (text2html.LAST_CONVERT.substring(0, 8) == "<strong>" && match != "{H"){
            // close strong
            replacement = "</strong>";
        }
        
        if (match in text2html.MARK_MAP){
            text2html.LAST_CONVERT = text2html.MARK_MAP[match];
            replacement += text2html.LAST_CONVERT;
        }
        
        return replacement;
    },

    parse_html: function(string){
        // Parses a string, replace markup with html
        
        // Convert html codes.
        string = string.replace(text2html.REGEXP_HTML, text2html.convert_html);

        // Convert marks
        string = string.replace(text2html.REGEXP_MARK, text2html.convert_mark);
        
        return string;
    },
};

// Compile RegExps.
text2html.REGEXP_HTML.compile(text2html.REGEXP_HTML);

var mark_pattern = new Array();
for (mark in text2html.MARK_MAP){
    mark = mark.replace(/\[/, "\\[");
    mark = mark.replace(/\*/, "\\*");
    mark_pattern.push(mark);
}
mark_pattern = mark_pattern.join("|");
mark_pattern = new RegExp(mark_pattern, "g");
text2html.REGEXP_MARK.compile(mark_pattern);

