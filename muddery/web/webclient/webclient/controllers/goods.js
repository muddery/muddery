
var _ = parent._;
var text2html = parent.text2html;
var net_settings = parent.net_settings;
var commands = parent.commands;

var controller = {
	
	_dbref: null,
	
	getObject: function() {
		return this._dbref;
	},

    // close popup box
    doClosePopupBox: function() {
        parent.controller.openShop();
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
			var url = net_settings.resource_url + icon;
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
