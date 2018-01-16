//@ sourceURL=/controller/skills.js

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
	$("#view_desc").text($$("DESC"));
}

/*
 * Event then the user clicks the skill link.
 */
Controller.prototype.onLook = function(event) {
    var dbref = $(this).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set skills' data.
 */
Controller.prototype.setSkills = function(skills) {
    this.clearElements("#skill_list");
    var template = $("#skill_list>.template");
    
    for (var i in skills) {
        var obj = skills[i];
        var item = this.cloneTemplate(template);

        item.find(".skill_name")
            .data("dbref", obj["dbref"])
        	.text(obj["name"]);
            
        if (obj["icon"]) {
            item.find(".img_icon").attr("src", $$.settings.resource_url + obj["icon"]);
        	item.find(".skill_icon").show();
        }
        else {
        	item.find(".skill_icon").hide();
        }

		var desc = $$.text2html.parseHtml(obj["desc"]);
        item.find(".skill_desc").html(desc);
        
        item.find("a").bind("click", this.onLook);
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
