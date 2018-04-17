
if (typeof(require) != "undefined") {
    require("../controllers/muddery_combat.js");
}

/*
 * Derive from the base class.
 */
Combat = function(el) {
	MudderyCombat.call(this, el);
}

Combat.prototype = prototype(MudderyCombat.prototype);
Combat.prototype.constructor = Combat;

/*
 * Update character's status.
 */
Combat.prototype.updateStatus = function(status) {
	for (var key in status) {
		var item_id = "#combat_char_" + key.slice(1) + ">div.status";
		$(item_id).text(status[key]["hp"] + "/" + status[key]["max_hp"]);

		if (this.self_dbref == key) {
		    $("#combat_status").text("HP:" + status[key]["hp"] + "/" + status[key]["max_hp"]
		                        + " MP:" + status[key]["mp"] + "/" + status[key]["max_mp"]);
		}
	}
}