//@ sourceURL=/controller/muddery_information.js

/*
 * Derive from the base class.
 */
function MudderyInformation() {
	BaseController.call(this);
}

MudderyInformation.prototype = prototype(BaseController.prototype);
MudderyInformation.prototype.constructor = MudderyInformation;

/*
 * Reset the view's language.
 */
MudderyInformation.prototype.resetLanguage = function() {
    $("#view_head").text($$("HEAD: "));
    $("#view_hand").text($$("HAND: "));
    $("#view_chest").text($$("CHEST: "));
    $("#view_leg").text($$("LEG: "));
}

/*
 * Bind events.
 */
MudderyInformation.prototype.bindEvents = function() {
	this.onClick("#box_equipment", "a", this.onLook);
}

/*
 * Event when clicks the object link.
 */
MudderyInformation.prototype.onLook = function(element) {
    var dbref = $(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set player's basic information.
 */
MudderyInformation.prototype.setInfo = function(name, icon) {
    $("#name").text(name);
    if (icon) {
        var url = $$.settings.resource_url + icon;
        $("#obj_icon").attr("src", url)
                      .show();
    }
    else {
        $("#obj_icon").hide();
    }
}

/*
 * Set player character's information.
 */
MudderyInformation.prototype.setStatus = function(status) {
    this.clearElements("#attributes");
    var template = $("#attributes>div.template");

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
        var item = this.cloneTemplate(template);
        item.attr("id", "info_" + key);

        var value = obj["value"];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in status) {
            // Add max value.
            var max_value = status[max_key]["value"];

            if (max_value == null || typeof(max_value) == "undefined") {
                max_value = "--";
            }
            else if (max_value == 0 && value == 0) {
                value = "--";
                max_value = "--";
            }

            value = value + "/" + max_value;
        }

        item.find(".attr_name").text(obj["name"]);
        item.find(".attr_value").text(value);
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
}

/*
 * Set player character's information in combat.
 */
MudderyInformation.prototype.setCombatStatus = function(status) {
    for (var key in status) {
        if (key.substring(0, 4) == "max_") {
            var relative_key = key.substring(4);
            if (relative_key in status) {
                // Value and max value will show in the same line, so skip max.
                continue;
            }
        }

        var item = $("#info_" + key);

        var value = status[key];
        if (value == null || typeof(value) == "undefined") {
            value = "--";
        }

        var max_key = "max_" + key;
        if (max_key in status) {
            // Add max value.
            var max_value = status[max_key];

            if (max_value == null || typeof(max_value) == "undefined") {
                max_value = "--";
            }
            else if (max_value == 0 && value == 0) {
                value = "--";
                max_value = "--";
            }

            value = value + "/" + max_value;
        }

        item.find(".attr_value").text(value);
    }
}

/*
 * Set player's equipments.
 */
MudderyInformation.prototype.setEquipments = function(equipments) {
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
}
