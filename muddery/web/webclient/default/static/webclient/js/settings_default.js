
var settings_default = {
    // language file's pathname
    language: '',

    // map settings
    map_room_size: 40,

    map_scale: 75,

    // command box
    show_command: false,
};

var settings_merge = settings_default;
for (key in settings) {
    settings_merge[key] = settings[key];
}
settings = settings_merge;

