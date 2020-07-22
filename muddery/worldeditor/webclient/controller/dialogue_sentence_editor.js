
/*
 * Derive from the base class.
 */
DialogueSentencesEditor = function() {
	CommonEditor.call(this);

    this.event_fields = [];
    this.event_table = "event_data";
}

DialogueSentencesEditor.prototype = prototype(CommonEditor.prototype);
DialogueSentencesEditor.prototype.constructor = DialogueSentencesEditor;

DialogueSentencesEditor.prototype.init = function() {
    this.dialogue_key = utils.getQueryString("dialogue");
    CommonEditor.prototype.init.call(this);
}

/***********************************
 *
 * Events
 *
 ***********************************/
DialogueSentencesEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-event").on("click", this.onAddEvent);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);
}

DialogueSentencesEditor.prototype.onEditEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "event";
        var args = {
            trigger: controller.obj_key,
             typeclass: controller.obj_typeclass,
        }
        window.parent.controller.editRecord(editor, controller.event_table, record_id, args);
    }
}

DialogueSentencesEditor.prototype.onDeleteEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteEvent,
                                     {record: record_id});
}

DialogueSentencesEditor.prototype.confirmDeleteEvent = function(e) {
    window.parent.controller.hideWaiting();

    var record_id = e.data.record;
    service.deleteRecord(controller.event_table, record_id, controller.deleteEventSuccess, controller.failedCallback);
}

DialogueSentencesEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
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
