
var settings_default = {

    language: '',

    map_room_size: 40,

    map_scale: 75,
};

var settings_merge = settings_default;
for (key in settings) {
    settings_merge[key] = settings[key];
}
settings = settings_merge;

