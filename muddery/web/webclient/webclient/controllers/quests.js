//@ sourceURL=/controller/quests.js

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
	$("#view_objective").text($$("OBJECTIVE"));
}

/*
 * Event when clicks the quest link.
 */
Controller.prototype.onLook = function(event) {
    var dbref = $(this).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set the player's quests.
 */
Controller.prototype.setQuests = function(quests) {
	this.clearElements("#quest_list");
    var template = $("#quest_list>tr.template");
    
	for (var i in quests) {
		var quest = quests[i];
		var item = this.cloneTemplate(template);

		item.find(".quest_name")
			.data("dbref", quest["dbref"])
			.text(quest["name"])
			.bind("click", this.onLook);
		
		var desc = $$.text2html.parseHtml(quest["desc"]);
		item.find(".quest_desc").html(desc);
		
		this.addObjectives(item, quest["objectives"]);
	}
}

/*
 * Add quest's objectives.
 */
Controller.prototype.addObjectives = function(container, objectives) {
	var template = container.find(".quest_objective>p.template");
	for (var i in objectives) {
		var item = this.cloneTemplate(template);

		if ("desc" in objectives[i]) {
			item.text(objectives[i]["desc"]);
		}
		else {
			item.text(objectives[i]["target"] + " " +
					  objectives[i]["object"] + " " +
					  objectives[i]["accomplished"] + "/" +
					  objectives[i]["total"]);
		}
	}
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
