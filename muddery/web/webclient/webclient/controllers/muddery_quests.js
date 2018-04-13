
if (typeof(require) != "undefined") {
    require("./base_controller.js");
}

/*
 * Derive from the base class.
 */
function MudderyQuests(el) {
	BaseController.call(this, el);
	
	this.paginator = new Paginator("#quests_wrapper");
}

MudderyQuests.prototype = prototype(BaseController.prototype);
MudderyQuests.prototype.constructor = MudderyQuests;

/*
 * Reset the view's language.
 */
MudderyQuests.prototype.resetLanguage = function() {
	this.select("#quests_view_name").text($$.trans("NAME"));
	this.select("#quests_view_desc").text($$.trans("DESC"));
	this.select("#quests_view_objective").text($$.trans("OBJECTIVE"));
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
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Event then the window resizes.
 */
MudderyQuests.prototype.onResize = function(element) {
	var height = $(window).innerHeight() - this.select("#quests_wrapper").offset().top - 16;
	this.paginator.tableHeight(height);
}

/*
 * Set the player's quests.
 */
MudderyQuests.prototype.setQuests = function(quests) {
	this.clearElements("#quest_list");
    var template = this.select("#quest_list>tr.template");
    
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
	
	var height = $(window).innerHeight() - this.select("#quests_wrapper").offset().top - 16;
	this.paginator.refresh(height);
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
