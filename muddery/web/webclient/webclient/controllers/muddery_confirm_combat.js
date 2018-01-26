//@ sourceURL=/controller/muddery_confirm_combat.js

/*
 * Derive from the base class.
 */
function MudderyConfirmCombat() {
	BaseController.call(this);
	
    this.prepare_time = 0;
    this.interval_id = null;
    this.confirmed = false;
}

MudderyConfirmCombat.prototype = prototype(BaseController.prototype);
MudderyConfirmCombat.prototype.constructor = MudderyConfirmCombat;

/*
 * Reset the view's language.
 */
MudderyConfirmCombat.prototype.resetLanguage = function() {
	$("#popup_body").text($$("Found an opponent."));
	$("#button_confirm").text($$("Confirm"));
}
	
/*
 * Bind events.
 */
MudderyConfirmCombat.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onRejectCombat);
    this.onClick("#button_confirm", this.onConfirmCombat);
}

/*
 * Event when clicks the confirm button.
 */
MudderyConfirmCombat.prototype.onConfirmCombat = function(element) {
	if (this.confirmed) {
		return;
	}
	this.confirmed = true;

	$$.commands.confirmCombat();

	$("#popup_body").text($$("Confirmed."));
	$("#button_confirm").hide();
	refreshPrepareTime();
}
	
/*
 * Event when clicks the close button.
 */
MudderyConfirmCombat.prototype.onRejectCombat = function(element) {
	if (this.confirmed) {
		return;
	}

	$$.commands.rejectCombat();
	this.closeBox();
}
	
/*
 * Set count down time.
 */
MudderyConfirmCombat.prototype.setTime = function(time) {
	this.confirmed = false;
	this.prepare_time = new Date().getTime() + time * 1000;
	$("#time").text(parseInt(time - 1) + $$(" seconds to confirm."));

	this.interval_id = window.setInterval("refreshPrepareTime()", 1000);
}

/*
 * Close this box.
 */
MudderyConfirmCombat.prototype.closeBox = function() {
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}

	$$.controller.closePrepareMatchBox();
}

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
