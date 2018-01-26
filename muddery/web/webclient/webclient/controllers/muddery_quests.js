//@ sourceURL=/controller/muddery_quests.js

/*
 * Derive from the base class.
 */
function MudderyQuests() {
	BaseController.call(this);
}

MudderyQuests.prototype = prototype(BaseController.prototype);
MudderyQuests.prototype.constructor = MudderyQuests;

/*
 * Reset the view's language.
 */
MudderyQuests.prototype.resetLanguage = function() {
	$("#view_name").text($$("NAME"));
	$("#view_desc").text($$("DESC"));
	$("#view_objective").text($$("OBJECTIVE"));
}

/*
 * Bind events.
 */
MudderyQuests.prototype.bindEvents = function() {
	this.onClick("#quest_list", ".quest_name", this.onLook);
}

/*
 * Event when clicks the quest link.
 */
MudderyQuests.prototype.onLook = function(element) {
    var dbref = $(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set the player's quests.
 */
MudderyQuests.prototype.setQuests = function(quests) {
	this.clearElements("#quest_list");
    var template = $("#quest_list>tr.template");
    
	for (var i in quests) {
		var quest = quests[i];
		var item = this.cloneTemplate(template);

		item.find(".quest_name")
			.data("dbref", quest["dbref"])
			.text(quest["name"]);
		
		var desc = $$.text2html.parseHtml(quest["desc"]);
		item.find(".quest_desc").html(desc);
		
		this.addObjectives(item, quest["objectives"]);
	}
}

/*
 * Add quest's objectives.
 */
MudderyQuests.prototype.addObjectives = function(container, objectives) {
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
