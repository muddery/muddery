//@ sourceURL=/controller/shop.js

/*
 * Derive from the base class.
 */
function MudderyShop(root_controller) {
	BaseController.call(this, root_controller);
	
	this.goods = [];
}

MudderyShop.prototype = prototype(BaseController.prototype);
MudderyShop.prototype.constructor = MudderyShop;

/*
 * Reset the view's language.
 */
MudderyShop.prototype.resetLanguage = function() {
	$("#header_name").text($$("NAME"));
	$("#header_price").text($$("PRICE"));
	$("#header_desc").text($$("DESC"));
}

/*
 * Bind events.
 */
MudderyShop.prototype.bindEvents = function() {
	this.onClick("#close_box", this.onClose);
	this.onClick("#goods_list", ".div_name", this.onLook);
}
	
/*
 * Event when clicks the close button.
 */
MudderyShop.prototype.onClose = function(element) {
    $$.controller.doClosePopupBox();
}

/*
 * Event then the user clicks the skill link.
 */
MudderyShop.prototype.onLook = function(element) {
	var dbref = $(element).data("dbref");
	for (var i in this.goods) {
		if (dbref == this.goods[i]["dbref"]) {
			var goods = this.goods[i];
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
MudderyShop.prototype.setShop = function(name, icon, desc, goods) {
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

	// clear shop
	this.clearElements("#goods_list");
	var template = $("#goods_list>.template");	

	// set goods
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
			.data("dbref", obj["dbref"]);

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
