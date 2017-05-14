
var LOCAL_STRING = {};

var language_dict = {
    "en-us": local_string_en_us,
    "zh-cn": local_string_zh_cn,
}

function _(str) {
    if (str in LOCAL_STRING) {
        return LOCAL_STRING[str];
    }

    return str;
};
