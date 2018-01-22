//@ sourceURL=/controller/dialogue.js

/*
 * Derive from the base class.
 */
function MudderyDialogue(root_controller) {
	BaseController.call(this, root_controller);
	
	this.target = null;
}

MudderyDialogue.prototype = prototype(BaseController.prototype);
MudderyDialogue.prototype.constructor = MudderyDialogue;

/*
 * Bind events.
 */
MudderyDialogue.prototype.bindEvents = function() {
    this.onClick("#close_box", this.onClose);
    this.onClick("#bottom_button", this.onSelectDialogue);
    this.onClick("#dialogue_body", "a", this.onSelectDialogue);
}

/*
 * Event when clicks the close button.
 */
MudderyDialogue.prototype.onClose = function(element) {
    $$.controller.doClosePopupBox();
}

/*
 * Event when click a dialogue.
 */
MudderyDialogue.prototype.onSelectDialogue = function(element) {
	var dialogue = $(element).data("dialogue");
	var sentence = $(element).data("sentence");
	var npc = $(element).data("npc");
	if (dialogue) {
		$$.commands.doDialogue(dialogue, sentence, npc);
	}
}

/*
 * Event when objects moved out from the current place.
 */
MudderyDialogue.prototype.onObjsMovedOut = function(objects) {
    for (var key in objects) {
        for (var i in objects[key]) {
            if (objects[key][i]["dbref"] == this.dbref) {
                this.onClose();
                return;
            }
        }
    }
}

/*
 * Set dialogue's data.
 */
MudderyDialogue.prototype.setDialogues = function(dialogues, escapes) {
	this.clearDialogues();

	if (dialogues.length == 0) {
		return;
	}
	
	this.target = dialogues[0]["npc"];

	if (dialogues[0]["can_close"]) {
		$("#close_box").show();
	}
	else {
		$("#close_box").hide();
	}

	// speaker
	var speaker = $$.text2html.parseHtml(dialogues[0]["speaker"]);
	if (!speaker) {
		// placeholder
		speaker = "&nbsp;";
	}
	$("#header").html(speaker);

	// add icon
	if (dialogues[0]["icon"]) {
		$("#img_icon").attr("src", $$.settings.resource_url + dialogues[0]["icon"]);
		$("#div_icon").show();
	}
	else {
		$("#div_icon").hide();
	}

	// set contents and buttons
	try {
		if (dialogues.length == 1) {
			// Only one sentence.
			var dlg = dialogues[0];

			var content = $$.text2html.parseHtml(dlg["content"]);
			content = $$.escape.parse(content, escapes);
			$("#dialogue_content").html(content);
			$("#dialogue_content").show();

			$("#bottom_button")
				.data("npc", dlg["npc"])
				.data("dialogue", dlg["dialogue"])
				.data("sentence", dlg["sentence"])
				.text($$("Next"));
		}
		else {
			var template = $("#dialogue_body>p.template");
			for (var i in dialogues) {
				var dlg = dialogues[i];

				var content = $$.text2html.parseHtml(dlg["content"]);
				content = $$.escape.parse(content, escapes);

				var item = this.cloneTemplate(template);
				item.find("a")
					.data("npc", dlg["npc"])
					.data("dialogue", dlg["dialogue"])
					.data("sentence", dlg["sentence"])
					.html(content);
			}

			$("#bottom_button").text($$("Select One"));
		}
	}
	catch(error) {
		console.error(error.message);
	}
}

/*
 * Clear all contents.
 */
MudderyDialogue.prototype.clearDialogues = function() {
	// Remove all dialogues.
	$("#header").empty();

	$("#div_icon").hide();
	$("#img_icon").removeAttr("src");

	$("#dialogue_content").empty();
	$("#dialogue_body>p:not(.template)").remove();

	$("#bottom_button")
		.removeData("npc")
		.removeData("dialogue")
		.removeData("sentence")
		.removeAttr("onClick")
		.empty();
}
