
var controller = {

    // Set player's basic information
    setInfo: function(name, icon) {
        $("#name").text(name);
        $("#obj_icon").attr("src", icon);
    },

    // Set player character's information
    setStatus: function(level, exp, max_exp, hp, max_hp, attack, defence) {
        var hp_str = hp + "/" + max_hp;

        var exp_str = "--";
        if (max_exp > 0) {
            exp_str = exp + "/" + max_exp;
        }

        $("#level").text(level);
        $("#exp").text(exp_str);
        $("#hp").text(hp_str);
        $("#attack").text(attack);
        $("#defence").text(defence);
    },

    // Set player's equipments.
    setEquipments(equipments) {
        for (var pos in equipments) {
            var equip = equipments[pos];
            var args = "";
            var name = "";
            if (equip) {
                args = equip["dbref"];
                name = equip["name"];
            }

            $("#" + pos)
                .attr("cmd_name", "look")
                .attr("cmd_args", args)
                .html(name);
        }
    },
};
