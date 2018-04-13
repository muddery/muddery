
if (typeof(require) != "undefined") {
    require("../css/inventory.css");

    require("../controllers/base_controller.js");
    require("../utils/paginator.js");
}

/*
 * Derive from the base class.
 */
MudderyInventory = function(el) {
	BaseController.call(this, el);

	this.paginator = new Paginator("#inv_inventory_wrapper");
}

MudderyInventory.prototype = prototype(BaseController.prototype);
MudderyInventory.prototype.constructor = MudderyInventory;

/*
 * Reset the view's language.
 */
MudderyInventory.prototype.resetLanguage = function() {
    this.select("#inv_view_name").text($$.trans("NAME"));
    this.select("#inv_view_number").text($$.trans("NUM"));
    this.select("#inv_view_desc").text($$.trans("DESC"));
}

/*
 * Bind events.
 */
MudderyInventory.prototype.bindEvents = function() {
	this.onClick("#inv_inventory_items", ".obj_name", this.onLook);
}
            
/*
 * Event when clicks the object link.
 */
MudderyInventory.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Event then the window resizes.
 */
MudderyInventory.prototype.onResize = function(element) {
	var height = $(window).innerHeight() - this.select("#inv_inventory_wrapper").offset().top - 16;
	this.paginator.tableHeight(height);
}

/*
 * Set inventory's data.
 */
MudderyInventory.prototype.setInventory = function(inventory) {
    this.clearElements("#inv_inventory_items");
    var template = this.select("#inv_inventory_items>tr.template");

    for (var i in inventory) {
        var obj = inventory[i];
        var item = this.cloneTemplate(template);

        item.find(".obj_name")
            .data("dbref", obj["dbref"])
            .html($$.text2html.parseHtml(obj["name"]));

        if (obj["icon"]) {
            item.find(".img_icon").attr("src", settings.resource_url + obj["icon"]);
            item.find(".obj_icon").show();
        }
        else {
            item.find(".obj_icon").hide();
        }

        var number = obj["number"];
        if ("equipped" in obj && obj["equipped"]) {
            number += $$.trans(" (equipped)");
        }
        item.find(".obj_number").text(number);

        item.find(".obj_desc").html($$.text2html.parseHtml(obj["desc"]));
    }

    var height = $(window).innerHeight() - this.select("#inv_inventory_wrapper").offset().top - 16;
	this.paginator.refresh(height);
}
