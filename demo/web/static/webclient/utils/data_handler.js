/*
Client Data Handler
*/

var data_handler = {
    character_dbref: "",
    character_name: "",
    current_target: "",
    name_list: {},
    dialogues_list: [],
    skill_cd_time: {},

    getEscapes: function() {
        return {"$PLAYER_NAME": this.character_name};
    },

    setSkills: function(skills) {
        var current_time = (new Date()).valueOf();

        for (var i in skills) {
            var key = skills[i]["key"];

            // cd_time in milliseconds
            var cd_time = current_time + skills[i]["cd_remain"] * 1000;
            this.skill_cd_time[key] = cd_time;
        }
    },

    setSkillCD: function(skill, cd, gcd) {
        // update skill's cd
        var current_time = (new Date()).valueOf();

        // cd_time in milliseconds
        var cd_time = current_time + cd * 1000;
        if (skill in this.skill_cd_time) {
            if (this.skill_cd_time[skill] < cd_time) {
                this.skill_cd_time[skill] = cd_time;
            }
        }
        else {
            this.skill_cd_time[skill] = cd_time;
        }

        var gcd_time = current_time + gcd * 1000;
        for (var key in this.skill_cd_time) {
            if (this.skill_cd_time[key] < gcd_time) {
                this.skill_cd_time[key] = gcd_time;
            }
        }
    },
};
