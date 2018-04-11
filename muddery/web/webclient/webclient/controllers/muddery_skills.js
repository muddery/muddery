
/*
 * Derive from the base class.
 */
function MudderySkills() {
	BaseController.call(this);

    this.paginator = new Paginator("#skills_wrapper");
}

MudderySkills.prototype = prototype(BaseController.prototype);
MudderySkills.prototype.constructor = MudderySkills;

/*
 * Reset the view's language.
 */
MudderySkills.prototype.resetLanguage = function() {
	this.select("#skill_view_name").text($$("NAME"));
	this.select("#skill_view_desc").text($$("DESC"));
}

/*
 * Bind events.
 */
MudderySkills.prototype.bindEvents = function() {
	this.onClick("#skill_list", ".skill_name", this.onLook);
	this.on(window, "resize", this.onResize);
}

/*
 * Event when clicks the skill link.
 */
MudderySkills.prototype.onLook = function(element) {
    var dbref = this.select(element).data("dbref");
    $$.commands.doLook(dbref);
}

/*
 * Event then the window resizes.
 */
MudderySkills.prototype.onResize = function(element) {
	var height = $(window).innerHeight() - this.select("#skills_wrapper").offset().top - 16;
	this.paginator.tableHeight(height);
}

/*
 * Set skills' data.
 */
MudderySkills.prototype.setSkills = function(skills) {
    this.clearElements("#skill_list");
    var template = this.select("#skill_list>.template");
    
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

	var height = $(window).innerHeight() - this.select("#skills_wrapper").offset().top - 16;
	this.paginator.refresh(height);
}
