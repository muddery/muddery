//@ sourceURL=/controller/combat.js

/*
 * Derive from the base class.
 */
function Combat() {
	MudderyCombat.call(this);
}

Combat.prototype = prototype(MudderyCombat.prototype);
Combat.prototype.constructor = Combat;

/*
 * Update character's status.
 */
Combat.prototype.updateStatus = function(status) {
	for (var key in status) {
		var item_id = "#char_" + key.slice(1) + ">div.status";
		$(item_id).text(status[key]["hp"] + "[" + status[key]["mp"] + "]");
	}
}
