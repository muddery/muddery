
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
    setStatus: function(status) {
        this.clearItems();
        var container = $("#attributes");
        var item_template = container.find("div.template");

        var attributes = [];
        for (var key in status) {
            attributes.push(status[key]);
        }
        attributes.sort(function(a, b){return a["order"] - b["order"]});

        for (var i in attributes) {
            var key = attributes[i]["key"];
            if (key.substring(0, 4) == "max_") {
                var relative_key = key.substring(4);
                if (relative_key in status) {
                    // Value and max value will show in the same line, so skip max.
                    continue;
                }
            }

            var obj = attributes[i];
            var item = item_template.clone()
	            .removeClass("template");

            var value = obj["value"];
            var max_key = "max_" + key;
            if (max_key in status) {
                // Add max value.
                var max_value = status[max_key]["value"];
                if (max_value <= 0) {
                    value = "--";
                }
                else {
                    value = value + "/" + max_value;
                }
            }

            item.find(".attr_name").text(obj["name"]);
            item.find(".attr_value").text(value);

			item.appendTo(container);
        }

        /*
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
        */
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

    clearItems: function() {
    	// Remove items that are not template.
    	$("#attributes>:not(.template)").remove();
    },
};

$(document).ready(function() {
	controller.onReady();
});