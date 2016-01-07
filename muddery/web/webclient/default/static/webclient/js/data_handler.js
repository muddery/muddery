/*
Client Data Handler
*/

var data_handler = {
    character_dbref: "",
    character_name: "",
    current_target: "",
    name_list: {},
    skill_cd_time: {},

    getEscapes: function() {
        return {"$PLAYER_NAME": this.character_name};
    },
};
