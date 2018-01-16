//@ sourceURL=/controller/shop.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
	
	this.goods = [];
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#header_name").text($$("NAME"));
	$("#header_price").text($$("PRICE"));
	$("#header_desc").text($$("DESC"));
}
	
/*
 * Event then the user clicks the close button.
 */
Controller.prototype.onClose = function(event) {
    $$.controller.doClosePopupBox();
}

/*
 * Bind events.
 */
BaseController.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
}

/*
 * Event then the user clicks the skill link.
 */
Controller.prototype.onLook = function(event) {
	var dbref = $(this).data("dbref");
	for (var i in controller.goods) {
		if (dbref == controller.goods[i]["dbref"]) {
			var goods = controller.goods[i];
			$$.controller.showGoods(goods["dbref"],
								   goods["name"],
				 				   goods["number"],
								   goods["icon"],
								   goods["desc"],
								   goods["price"],
								   goods["unit"]);
			break;
		}
	}
}

/*
 * Set shop's data.
 */
Controller.prototype.setShop = function(name, icon, desc, goods) {
	this.goods = goods || [];
		
	// add name
	$("#shop_name").html($$.text2html.parseHtml(name));

	// add icon
	if (icon) {
		var url = $$.settings.resource_url + icon;
		$("#img_icon").attr("src", url);
		$("#shop_icon").show();
	}
	else {
		$("#shop_icon").hide();
	}

	// add desc
	$("#shop_desc").html($$.text2html.parseHtml(desc));
		
	// set goods
	// clear shop
	this.clearElements("#goods_list");
	var template = $("#goods_list>.template");	

	for (var i in this.goods) {
		var obj = this.goods[i];
		var item = this.cloneTemplate(template);

		if (obj["icon"]) {
			item.find(".img_icon").attr("src", $$.settings.resource_url + obj["icon"]);
			item.find(".obj_icon").show();
		}
		else {
			item.find(".obj_icon").hide();
		}

		item.find(".div_name")
			.data("dbref", obj["dbref"])
			.bind("click", this.onLook);

		var goods_name = $$.text2html.parseHtml(obj["name"]);
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
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
