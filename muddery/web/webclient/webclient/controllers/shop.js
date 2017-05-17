
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;

var controller = {

	_goods: [],

    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
		$("#header_name").text(_("NAME"));
		$("#header_price").text(_("PRICE"));
		$("#header_desc").text(_("DESC"));
	},
	
    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },

	setShop: function(name, icon, desc, goods) {
		this._goods = goods;
		
		// add name
	    name = text2html.parseHtml(name);
	    $("#shop_name").html(name);

		// add icon
		if (icon) {
			var url = settings.resource_url + icon;
			$("#img_icon").attr("src", url);
			$("#shop_icon").show();
        }
        else {
            $("#shop_icon").hide();
        }

		// add desc
	    desc = text2html.parseHtml(desc);
		$("#shop_desc").html(desc);
		    
		// set goods
		// remove rolls that are not template..
    	$("#goods_list>:not(.template)").remove();
    	
    	var container = $("#goods_list");
		var item_template = container.find("tr.template");

		if (goods) {
            for (var i in goods) {
                var obj = goods[i];

				var item = item_template.clone()
                	.removeClass("template");

                if (obj["icon"]) {
            	    item.find(".img_icon").attr("src", settings.resource_url + obj["icon"]);
            	    item.find(".obj_icon").show();
                }
                else {
            	    item.find(".obj_icon").hide();
                }

                item.find(".div_name")
                    .data("dbref", obj["dbref"]);

				var goods_name = text2html.parseHtml(obj["name"]);
				item.find(".goods_name")
            		.html(obj["name"]);

            	if (obj["number"] == 1) {
            	    item.find(".number_mark")
            	        .hide();
            	}
            	else {
            	    item.find(".number_mark")
            	        .show();
                    item.find(".goods_number")
                	    .text(obj["number"]);
                }

                item.find(".price")
                	.text(obj["price"]);
                	
                item.find(".unit")
                	.text(obj["unit"]);
                	
                item.appendTo(container);
            }
        }
	},

    showGoods: function(caller) {
    	var dbref = $(caller).data("dbref");
        for (var i in this._goods) {
            if (dbref == this._goods[i]["dbref"]) {
            	var goods = this._goods[i];
                parent_controller.showGoods(goods["dbref"],
                							goods["name"],
                							goods["number"],
                							goods["icon"],
                							goods["desc"],
                							goods["price"],
                							goods["unit"]);
                break;
            }
        }
    },
};

$(document).ready(function() {
	controller.onReady();
});
