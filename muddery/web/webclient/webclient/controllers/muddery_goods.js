
if (typeof(require) != "undefined") {
    require("./base_controller.js");
}

/*
 * Derive from the base class.
 */
function MudderyGoods(el) {
	BasePopupController.call(this, el);

	this.dbref = null;
}

MudderyGoods.prototype = prototype(BasePopupController.prototype);
MudderyGoods.prototype.constructor = MudderyGoods;

/*
 * Reset the view's language.
 */
MudderyGoods.prototype.resetLanguage = function() {
	$("#goods_button_buy").text($$.trans("Buy"));
}

/*
 * Bind events.
 */
MudderyGoods.prototype.bindEvents = function() {
    this.onClick("#goods_close_box", this.onClose);
    this.onClick("#goods_button_buy", this.onBuy);
}

/*
 * Event when clicks the close button.
 */
MudderyGoods.prototype.onClose = function(element) {
	$$.main.doClosePopupBox();
}

/*
 * Event when clicks the buy button.
 */
MudderyGoods.prototype.onBuy = function(element) {
    this.onClose();

    if (this.dbref) {
        $$.commands.buyGoods(this.dbref);
    }
}

/*
 * Set goods data.
 */
MudderyGoods.prototype.setGoods = function(dbref, name, number, icon, desc, price, unit) {
    this.dbref = dbref;

    // add name
    $("#goods_name").html($$.text2html.parseHtml(name));

    if (number == 1) {
        $("#goods_number_mark").hide();
    }
    else {
        $("#goods_number_mark").show();
        $("#goods_number").html(number);
    }

    // add icon
    if (icon) {
        var url = settings.resource_url + icon;
        $("#goods_img_icon").attr("src", url);
        $("#goods_div_icon").show();
    }
    else {
        $("#goods_div_icon").hide();
    }

    // add price
    $("#goods_price").text(price);
    $("#goods_unit").text(unit);

    // add desc
    $("#goods_desc").html($$.text2html.parseHtml(desc));
}
