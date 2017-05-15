
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
	_dbref: null,

	// on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#view_button_buy").text(_("Buy"));
	},
	
	getObject: function() {
		return this._dbref;
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.openShop();
    },

	setGoods: function(dbref, name, number, icon, desc, price, unit) {
		this._dbref = dbref;
		
		// add name
	    name = text2html.parseHtml(name);
	    $("#name").html(name);

        if (number == 1) {
            $("#number_mark").hide();
        }
        else {
            $("#number_mark").show();
	        $("#number").html(number);
	    }

		// add icon
		if (icon) {
			var url = settings.resource_url + icon;
			$("#img_icon").attr("src", url);
			$("#div_icon").show();
        }
        else {
            $("#div_icon").hide();
        }
        
        // add price
        $("#price").text(price);
        $("#unit").text(unit);

		// add desc
	    desc = text2html.parseHtml(desc);
		$("#desc").html(desc);
	},

    buyGoods: function(caller) {
        this.doClosePopupBox();

        if (this._dbref) {
            commands.buyGoods(this._dbref);
        }
    },
};

$(document).ready(function() {
	controller.onReady();
});