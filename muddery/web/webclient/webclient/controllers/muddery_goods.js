//@ sourceURL=/controller/muddery_goods.js

/*
 * Derive from the base class.
 */
function MudderyGoods() {
	BaseController.call(this);

	this.dbref = null;
}

MudderyGoods.prototype = prototype(BaseController.prototype);
MudderyGoods.prototype.constructor = MudderyGoods;

/*
 * Reset the view's language.
 */
MudderyGoods.prototype.resetLanguage = function() {
	$("#button_buy").text($$("Buy"));
}

/*
 * Bind events.
 */
MudderyGoods.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
    this.onClick("#button_buy", this.onBuy);
}

/*
 * Event when clicks the close button.
 */
MudderyGoods.prototype.onClose = function(element) {
	$$.controller.doClosePopupBox();
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
    $("#name").html($$.text2html.parseHtml(name));

    if (number == 1) {
        $("#number_mark").hide();
    }
    else {
        $("#number_mark").show();
        $("#number").html(number);
    }

    // add icon
    if (icon) {
        var url = $$.settings.resource_url + icon;
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
    $("#desc").html($$.text2html.parseHtml(desc));
}
