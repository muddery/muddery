
var controller = {

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },

    setDialogues: function(dialogues, escapes) {
        this.clearDialogues();

        if (dialogues.length == 0) {
            return;
        }

        // speaker
        var speaker = text2html.parseHtml(dialogues[0]["speaker"]);
        if (!speaker) {
            // placeholder
            speaker = "&nbsp;";
        }
        $("#header").html(speaker);

        // add icon
        var icon = dialogues[0]["icon"];
        if (icon) {
            var url = settings.resource_location + icon;
            $("#img_icon").attr("src", url);
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
                var item_template = $("#body a.template");
                for (var i in dialogues) {
                    var dlg = dialogues[i];

                    var content = text2html.parseHtml(dlg["content"]);
                    content = escape.parse(content, escapes);

                    item_template.clone()
                        .removeClass("template")
                        .data("npc", dlg["npc"])
                        .data("dialogue", dlg["dialogue"])
                        .data("sentence", dlg["sentence"])
                        .html(content)
                        .appendTo(body);
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
        $("#img_icon")
            .removeAttr("src")
            .hide();

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
        parent.commands.doDialogue(dialogue, sentence, npc);
    },
};
