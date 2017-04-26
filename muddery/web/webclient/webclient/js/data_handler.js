/*
Client Data Handler
*/

var data_handler = {
    character_dbref: "",
    character_name: "",
    current_target: "",
    name_list: {},
    skill_cd_time: {},
    dialogue_target: "",
    dialogues_list: [],
    shop_data: {},

    getEscapes: function() {
        return {"$PLAYER_NAME": this.character_name};
    },
};
