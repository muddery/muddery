
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var commands = parent.commands;

var controller = {
    _prepare_time: 0,
    _interval_id: null,
    _confirmed: false,

    // on document ready
    onReady: function() {
        this.resetLanguage();

        $("#button_close").bind("click", this.onRejectCombat);
        $("#button_confirm").bind("click", this.onConfirmCombat);
    },

	// reset view's language
	resetLanguage: function() {
	    $("#popup_body").text(_("Found an opponent."));
		$("#button_confirm").text(_("Confirm"));
	},

	init: function(time) {
	    this._confirmed = false;
	    this._prepare_time = new Date().getTime() + time * 1000;
        $("#time").text(parseInt(time - 1));

        this._interval_id = window.setInterval("refreshPrepareTime()", 1000);
	},

	closeBox: function() {
	    if (this._interval_id != null) {
            this._interval_id = window.clearInterval(this._interval_id);
        }

        parent_controller.closePrepareMatchBox();
	},
	
	onConfirmCombat: function() {
	    if (controller._confirmed) {
	        return;
	    }
	    controller._confirmed = true;

	    commands.confirmCombat();

	    if (controller._interval_id != null) {
            controller._interval_id = window.clearInterval(controller._interval_id);
        }

        $("#time").text(_("Confirmed."));
	},
	
	onRejectCombat: function() {
	    if (controller._confirmed) {
	        return;
	    }

	    commands.rejectCombat();
	    controller.closeBox();
	},
};

$(document).ready(function() {
	controller.onReady();
});


function refreshPrepareTime() {
    var current_time = new Date().getTime();
    var remain_time = Math.floor((controller._prepare_time - current_time) / 1000);
    if (remain_time < 0) {
        remain_time = 0;
    }
    $("#time").text(parseInt(remain_time));
    
    if (remain_time <= 0) {
        controller.closeBox();
    }
};
