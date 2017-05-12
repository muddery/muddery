
var _ = parent._;
var text2html = parent.text2html;
var net_settings = parent.net_settings;
var escape = parent.escape;
var commands = parent.commands;

var controller = {

	_target: null,
	
	getTarget: function() {
		return this._target;
	},

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },

    setDialogues: function(dialogues, escapes, can_close) {
        this.clearDialogues();

        if (dialogues.length == 0) {
            return;
        }
        
        this._target = dialogues[0].npc;
        
    	if (can_close) {
    		$("#close_box").show();
    	}
    	else {
    		$("#close_box").hide();
    	}

        // speaker
        var speaker = text2html.parseHtml(dialogues[0]["speaker"]);
        if (!speaker) {
            // placeholder
            speaker = "&nbsp;";
        }
        $("#header").html(speaker);

        // add icon
        if (dialogues[0]["icon"]) {
            $("#img_icon").attr("src", net_settings.resource_url + dialogues[0]["icon"]);
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

                var content = text2html.parseHtml(dlg["content"]);
                content = escape.parse(content, escapes);
                $("#content").html(content);
                $("#content").show();

                $("#button")
                    .data("npc", dlg["npc"])
                    .data("dialogue", dlg["dialogue"])
                    .data("sentence", dlg["sentence"])
                    .attr("onClick", "controller.doDialogue(this)")
                    .text(_("Next"));
            }
            else {
                var body = $("#body");
                var item_template = $("#body>p.template");
                for (var i in dialogues) {
                    var dlg = dialogues[i];

                    var content = text2html.parseHtml(dlg["content"]);
                    content = escape.parse(content, escapes);

                    var item = item_template.clone()
                        .removeClass("template");

                    item.find("a")
                        .data("npc", dlg["npc"])
                        .data("dialogue", dlg["dialogue"])
                        .data("sentence", dlg["sentence"])
                        .html(content)

                    item.appendTo(body);
                }

                $("#button").text(_("Select One"));
            }
        }
        catch(error) {
            console.error(error.message);
        }
    },

    clearDialogues: function() {
        // Remove all dialogues.
        $("#header").empty();

        $("#div_icon").hide();
        $("#img_icon").removeAttr("src");

        $("#content").empty();
        $("#body>a:not(.template)").remove();

        $("#button")
            .removeData("npc")
            .removeData("dialogue")
            .removeData("sentence")
            .removeAttr("onClick")
            .empty();
    },

    doDialogue: function(caller) {
        this.doClosePopupBox();

        var dialogue = $(caller).data("dialogue");
        var sentence = $(caller).data("sentence");
        var npc = $(caller).data("npc");
        commands.doDialogue(dialogue, sentence, npc);
    },
};
