//@ sourceURL=/controller/inventory.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
    $("#view_name").text($$("NAME"));
    $("#view_number").text($$("NUM"));
    $("#view_desc").text($$("DESC"));
}

/*
 * Event when clicks the object link.
 */
Controller.prototype.onLook = function(event) {
    var dbref = $(this).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set inventory's data.
 */
Controller.prototype.setInventory = function(inventory) {
    this.clearElements("#inventory_items");
    var template = $("#inventory_items>tr.template");

    for (var i in inventory) {
        var obj = inventory[i];
        var item = this.cloneTemplate(template);

        item.find(".obj_name")
            .data("dbref", obj["dbref"])
            .text(obj["name"])
            .bind("click", this.onLook);

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

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
