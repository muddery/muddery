//@ sourceURL=/controller/honours.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);

	this.min_honour_level = 1;
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
    $("#button_fight").text($$("FIGHT"));
    $("#view_ranking").text($$("RANKING"));
    $("#view_name").text($$("NAME"));
    $("#view_honour").text($$("HONOUR"));
    $("#button_queue").text($$("QUEUE UP"));
    $("#button_quit").text($$("QUIT QUEUE"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#button_queue").bind("click", this.onQueueUpCombat);
    $("#button_quit").bind("click", this.onQuitCombatQueue);
}

/*
 * Event when clicks the queue up button.
 */
Controller.prototype.onQueueUpCombat = function() {
    if ($$.data_handler.character_level < controller.min_honour_level) {
        $$.controller.showAlert($$("You need to reach level ") + controller.min_honour_level + $$("."));
        return;
    }

    controller.queueUpCombat();
    $$.commands.queueUpCombat();
}

/*
 * Event when clicks the quit queue button.
 */
Controller.prototype.onQuitCombatQueue = function() {
	controller.quitCombatQueue();
    $$.commands.quitCombatQueue();
}

/*
 * Set the minimum level that a player can attend the honour combat.
 */
Controller.prototype.setMinHonourLevel = function(level) {
	this.min_honour_level = level;
}

/*
 * Set top characters.
 */
Controller.prototype.setRankings = function(rankings) {
    this.clearElements("#character_items");
    var template = $("#character_items>tr.template");

    for (var i in rankings) {
        var data = rankings[i];
        var item = this.cloneTemplate(template);

        item.find(".character_ranking")
            .text(data["ranking"]);

        item.find(".character_name")
            .text(data["name"]);

        item.find(".character_honour")
            .text(data["honour"]);
    }
}

/*
 * Set the queue up state.
 */
Controller.prototype.queueUpCombat = function() {
    $("#button_queue").hide();
    $("#button_quit").show();
}

/*
 * Set the quit queue state.
 */
Controller.prototype.quitCombatQueue = function() {
    $("#button_queue").show();
    $("#button_quit").hide();
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
