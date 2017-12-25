
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var commands = parent.commands;

var controller = {
    _prepare_time: 0,
    _interval_id: null,

    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
	},
	
    // close popup box
    doClosePopupBox: function() {
        commands.rejectCombat();
        parent_controller.doClosePopupBox();
    },

	setPrepareTime: function(time) {
	    this.prepare_time = new Date().getTime() + time;
        $("#time").text(parseInt(time));
        
        this._interval_id = window.setInterval("refreshPrepareTime()", 1000);
	},
	
	confirmCombat: function() {
	    commands.confirmCombat();
	},
	
	rejectCombat: function() {
	    commands.rejectCombat();
	},
};

$(document).ready(function() {
	controller.onReady();
});


function refreshPrepareTime() {
    var current_time = new Date().getTime();
    var remain_time = Math.floor((current_time - controller._prepare_time) / 1000);
    $("#time").text(parseInt(remain_time));
    
    if (current_time - controller._prepare_time <= 0) {
        commands.rejectCombat();
        if (this._interval_id != null) {
            this._interval_id = window.clearInterval(this._interval_id);
        }
    }
};
