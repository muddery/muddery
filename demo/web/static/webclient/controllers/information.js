
var _ = parent._;
var parent_controller = parent.controller;
var commands = parent.commands;
var settings = parent.settings;

var controller = {
    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_level").text(_("LEVEL: "));
		$("#view_exp").text(_("EXP: "));
		$("#view_hp").text(_("HP: "));
		$("#view_hunger").text(_("HUNGER: "));
		$("#view_attack").text(_("ATTACK: "));
		$("#view_defence").text(_("DEFENCE: "));
		$("#view_head").text(_("HEAD: "));
		$("#view_hand").text(_("HAND: "));
		$("#view_chest").text(_("CHEST: "));
		$("#view_leg").text(_("LEG: "));
	},
	
    // Set player's basic information
    setInfo: function(name, icon) {
        $("#name").text(name);
        var url = settings.resource_url + icon;
        $("#obj_icon").attr("src", url);
    },

    // Set player character's information
    setStatus: function(level, exp, max_exp, hp, max_hp, hunger, hungerMax, attack, defence) {
        var hp_str = hp + "/" + max_hp;

        var exp_str = "--";
        if (max_exp > 0) {
            exp_str = exp + "/" + max_exp;
        }
        var hunger_str = "--";
        if (hungerMax > 0){
            hunger_str = hunger + "/" + hungerMax;
        }

        $("#level").text(level);
        $("#exp").text(exp_str);
        $("#hp").text(hp_str);
        $("#hunger").text(hunger_str);
        $("#attack").text(attack);
        $("#defence").text(defence);
    },

    // Set player's equipments.
    setEquipments(equipments) {
        for (var pos in equipments) {
            var equip = equipments[pos];
            var dbref = "";
            var name = "";
            if (equip) {
                dbref = equip["dbref"];
                name = equip["name"];
            }

            $("#" + pos)
                .data("dbref", dbref)
                .html(name);
        }
    },

    doLook: function(caller) {
        var dbref = $(caller).data("dbref");
        commands.doLook(dbref);
    },
};

$(document).ready(function() {
	controller.onReady();
});