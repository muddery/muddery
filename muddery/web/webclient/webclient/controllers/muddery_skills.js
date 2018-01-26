//@ sourceURL=/controller/muddery_skills.js

/*
 * Derive from the base class.
 */
function MudderySkills() {
	BaseController.call(this);
}

MudderySkills.prototype = prototype(BaseController.prototype);
MudderySkills.prototype.constructor = MudderySkills;

/*
 * Reset the view's language.
 */
MudderySkills.prototype.resetLanguage = function() {
	$("#view_name").text($$("NAME"));
	$("#view_desc").text($$("DESC"));
}

/*
 * Bind events.
 */
MudderySkills.prototype.bindEvents = function() {
	this.onClick("#skill_list", ".skill_name", this.onLook);
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onLook = function(element) {
    var dbref = $(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Set skills' data.
 */
MudderySkills.prototype.setSkills = function(skills) {
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
	}
}
