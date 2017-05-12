
var LOCAL_STRING = {};

function _(str) {
    if (str in LOCAL_STRING) {
        return LOCAL_STRING[str];
    }

    return str;
};
