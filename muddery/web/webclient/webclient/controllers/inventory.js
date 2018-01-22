//@ sourceURL=/controller/inventory.js

/*
 * Derive from the base class.
 */
function MudderyInventory(root_controller) {
	BaseController.call(this, root_controller);
}

MudderyInventory.prototype = prototype(BaseController.prototype);
MudderyInventory.prototype.constructor = MudderyInventory;

/*
 * Reset the view's language.
 */
MudderyInventory.prototype.resetLanguage = function() {
    $("#view_name").text($$("NAME"));
    $("#view_number").text($$("NUM"));
    $("#view_desc").text($$("DESC"));
}

/*
 * Bind events.
 */
MudderyInventory.prototype.bindEvents = function() {
	this.onClick("#inventory_items", ".obj_name", this.onLook);
}
            
/*
 * Event when clicks the object link.
 */
MudderyInventory.prototype.onLook = function(element) {
    var dbref = $(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set inventory's data.
 */
MudderyInventory.prototype.setInventory = function(inventory) {
    this.clearElements("#inventory_items");
    var template = $("#inventory_items>tr.template");

    for (var i in inventory) {
        var obj = inventory[i];
        var item = this.cloneTemplate(template);

        item.find(".obj_name")
            .data("dbref", obj["dbref"])
            .text(obj["name"]);

        if (obj["icon"]) {
            item.find(".img_icon").attr("src", $$.settings.resource_url + obj["icon"]);
            item.find(".obj_icon").show();
        }
        else {
            item.find(".obj_icon").hide();
        }

        var number = obj["number"];
        if ("equipped" in obj && obj["equipped"]) {
            number += $$(" (equipped)");
        }
        item.find(".obj_number").text(number);

        item.find(".obj_desc").html($$.text2html.parseHtml(obj["desc"]));
    }
}
