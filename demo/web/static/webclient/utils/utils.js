
var util = {
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
};
