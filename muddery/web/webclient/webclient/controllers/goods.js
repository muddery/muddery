//@ sourceURL=/controller/honours.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);

	this.dbref = null;
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
	$("#button_buy").text($$("Buy"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
	$("#close_box").bind("click", this.onClose);
	$("#button_buy").bind("click", this.onBuy);
}

/*
 * Event when clicks the close button.
 */
Controller.prototype.onClose = function() {
	$$.controller.doClosePopupBox();
}

/*
 * Event when clicks the buy button.
 */
Controller.prototype.onBuy = function(caller) {
    controller.onClose();

    if (controller.dbref) {
        $$.commands.buyGoods(controller.dbref);
    }
}

/*
 * Set goods data.
 */
Controller.prototype.setGoods = function(dbref, name, number, icon, desc, price, unit) {
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

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});