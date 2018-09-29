
/*
 * Derive from the base class.
 */
DialogueSentencesEditor = function() {
	CommonEditor.call(this);

    this.event_key = "";
}

DialogueSentencesEditor.prototype = prototype(CommonEditor.prototype);
DialogueSentencesEditor.prototype.constructor = DialogueSentencesEditor;

DialogueSentencesEditor.prototype.init = function() {
    this.dialogue_key = utils.getQueryString("dialogue");
    CommonEditor.prototype.init.call(this);
}

DialogueSentencesEditor.prototype.setFields = function() {
    // Set fields.
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        // Users can not set the event's key and trigger object.
        if (field.name == "dialogue") {
            field.type = "Hidden";
            field.value = this.dialogue_key;
        }

        var controller = this.createFieldController(field);
        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}
