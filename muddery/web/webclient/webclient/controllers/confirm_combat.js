//@ sourceURL=/controller/confirm_combat.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
    this.prepare_time = 0;
    this.interval_id = null;
    this.confirmed = false;
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#popup_body").text($$("Found an opponent."));
	$("#button_confirm").text($$("Confirm"));
}
	
/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#close_box").bind("click", this.onRejectCombat);
    $("#button_confirm").bind("click", this.onConfirmCombat);
}

/*
 * Event when clicks the confirm button.
 */
Controller.prototype.onConfirmCombat = function() {
	if (controller.confirmed) {
		return;
	}
	controller.confirmed = true;

	$$.commands.confirmCombat();

	$("#popup_body").text($$("Confirmed."));
	$("#button_confirm").hide();
	refreshPrepareTime();
}
	
/*
 * Event when clicks the close button.
 */
Controller.prototype.onRejectCombat = function() {
	if (controller.confirmed) {
		return;
	}

	$$.commands.rejectCombat();
	controller.closeBox();
}
	
/*
 * Set count down time.
 */
Controller.prototype.setTime = function(time) {
	this.confirmed = false;
	this.prepare_time = new Date().getTime() + time * 1000;
	$("#time").text(parseInt(time - 1) + $$(" seconds to confirm."));

	this.interval_id = window.setInterval("refreshPrepareTime()", 1000);
}

/*
 * Close this box.
 */
Controller.prototype.closeBox = function() {
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}

	$$.controller.closePrepareMatchBox();
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});

function refreshPrepareTime() {
    var current_time = new Date().getTime();
    var remain_time = Math.floor((controller.prepare_time - current_time) / 1000);
    if (remain_time < 0) {
        remain_time = 0;
    }
    var text;
    if (controller.confirmed) {
        text = $$(" seconds to start the combat.");
    }
    else {
        text = $$(" seconds to confirm.");
    }

    $("#time").text(parseInt(remain_time) + text);
    
    if (remain_time <= 0) {
        controller.closeBox();
    }
}
