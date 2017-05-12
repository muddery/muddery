
var client_settings = {
    // default values

    language: "en-us",

    // map settings
    map_room_size: 40,

    map_scale: 75,

    // command box
    show_command_box: false,

    // can close dialogue box
    can_close_dialogue: false,
    
    // social box
    show_social_box: false,
    
    // game title
    game_title: '',
    
    // types of players messages
    msg_types: {
    	"say": "Say",
    	"command": "Cmd",
    },

    setValues: function(values) {
        for (var key in values) {
            this[key] = values[key];
        }

        // language
        $.getScript("./js/lang/" + this.language + "/strings.js");

		// command box
        if (this.show_command_box) {
            $("#msg_type_command").css("display", "");
        }
        else {
            $("#msg_type_command").css("display", "none");
        }
        
        // social ui
        var login = $("#tab_scene").css("display");
        if (self.show_social_box && login) {
        	$("#tab_social").css("display", "");
        }
        else {
        	$("#tab_social").css("display", "none");
        }
        
		// game's name
        if (this.game_name) {
            $("#game_title").text(this.game_name);
        }
    },
};