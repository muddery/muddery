
var LOCAL_STRING = {};

function LS(str) {
    if (str in LOCAL_STRING) {
        return LOCAL_STRING[str];
    }
    
    return str;
};
