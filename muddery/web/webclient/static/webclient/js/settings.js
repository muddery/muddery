
var settings = {
    // default values
    // language file's pathname
    language: '',

    // map settings
    map_room_size: 40,

    map_scale: 75,

    // command box
    show_command_box: false,

    // can close dialogue box
    can_close_dialogue: false,

    set: function(values) {
        for (var key in values) {
            this[key] = values[key];
        }

        if (this.show_command_box) {
            $("#item_command").css("display", "");
        } else {
            $("#item_command").css("display", "none");
        }
    },
};