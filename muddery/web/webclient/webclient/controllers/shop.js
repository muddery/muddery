
var controller = {

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },

	setShop: function(name, icon, desc, goods) {
		// add name
	    name = text2html.parseHtml(name);
	    $("#shop_name").html(name);

		// add icon
		if (icon) {
			var url = settings.resource_location + icon;
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
    	
    	var content = $("#goods_list");
		var item_template = content.find("tr.template");

		if (goods) {
            for (var i in goods) {
                var obj = goods[i];

				var item = item_template.clone()
                	.removeClass("template");

				var goods_name = text2html.parseHtml(obj["name"]);

				item.find(".goods_name")
                	.data("dbref", obj["dbref"])
            		.html(obj["name"]);
            	
                item.find(".goods_number")
                	.text(obj["number"]);
                
                var price = obj["price"] + " " + obj["unit"];
                item.find(".goods_price")
                	.text(price);
            }
        }
	},

	addButtons: function(data) {
		// remove rolls that are not template..
    	$("#button_content>:not(.template)").remove();
    	
    	var content = $("#button_content");
		var item_template = content.find("button.template");

		var has_button = false;
		if (data) {
            for (var i in data) {
                var cmd = data[i];

                var name = text2html.parseHtml(cmd["name"]);
                item_template.clone()
                    .removeClass("template")
                    .data("cmd_name", cmd["cmd"])
                    .data("cmd_args", cmd["args"])
                    .html(name)
                    .appendTo(content);

                has_button = true;
            }
        }
    },

    doCommandLink: function(caller) {
        this.doClosePopupBox();

        var cmd = $(caller).data("cmd_name");
        var args = $(caller).data("cmd_args");
        if (cmd) {
            parent.commands.doCommandLink(cmd, args);
        }
    },
};
