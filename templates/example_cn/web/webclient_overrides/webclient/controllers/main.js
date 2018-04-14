
if (typeof(require) != "undefined") {
    require("../controllers/muddery_main.js");
}

/*
 * Derive from the base class.
 */
Main = function(el) {
	MudderyMain.call(this, el);
	
	this.puppet = false;
    this.solo_mode = false;
	this.message_type = null;
	this.waiting_begin = 0;
}

Main.prototype = prototype(MudderyMain.prototype);
Main.prototype.constructor = Main;


//////////////////////////////////////////
//
// Prompt Bar
//
//////////////////////////////////////////
Main.prototype.setPromptBar = function() {
    this.clearPromptBar();

    var template = $("#prompt_content>.template");

    var item = this.cloneTemplate(template);
    item.attr("id", "prompt_name");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_level");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_exp");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_hp");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_mp");

    item = this.cloneTemplate(template);
    item.attr("id", "prompt_queue");
}

/*
 *  Set the player's status.
 */
Main.prototype.setStatus = function(status) {
	$$.data_handler.character_level = status["level"]["value"];
	$("#prompt_level").text("Lv:" + status["level"]["value"]);

	var exp_str = "";
	if (status["max_exp"]["value"] > 0) {
		exp_str = status["exp"]["value"] + "/" + status["max_exp"]["value"];
	}
	else {
		exp_str = "--/--";
	}
	$("#prompt_exp").text("Ex:" + exp_str);

	var hp_str = status["hp"]["value"] + "/" + status["max_hp"]["value"];
	$("#prompt_hp").text("HP:" + hp_str);

	var mp_str = status["mp"]["value"] + "/" + status["max_mp"]["value"];
	$("#prompt_mp").text("MP:" + mp_str);

	$$.component.information.setStatus(status);
}

/*
 *  Set the player's status in combat.
 */
Main.prototype.setCombatStatus = function(status) {
	var hp_str = status["hp"] + "/" + status["max_hp"];
	$("#prompt_hp").text("HP:" + hp_str);

	var mp_str = status["mp"] + "/" + status["max_mp"];
	$("#prompt_mp").text("MP:" + mp_str);

	$$.component.information.setCombatStatus(status);
}
