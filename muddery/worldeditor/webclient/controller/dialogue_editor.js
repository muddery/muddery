
/*
 * Derive from the base class.
 */
DialogueEditor = function() {
	CommonEditor.call(this);

    this.dialogue_key = "";
    this.sentence_fields = [];

    this.event_fields = [];
    this.event_table = "event_data";
}

DialogueEditor.prototype = prototype(CommonEditor.prototype);
DialogueEditor.prototype.constructor = DialogueEditor;


DialogueEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-sentence").on("click", this.addSentence);
    $("#sentence-table").on("click", ".edit-row", this.onEditSentence);
    $("#sentence-table").on("click", ".delete-row", this.onDeleteSentence);

    $("#add-event").on("click", this.onAddEvent);
    $("#event-table").on("click", ".edit-row", this.onEditEvent);
    $("#event-table").on("click", ".delete-row", this.onDeleteEvent);
}

DialogueEditor.prototype.onImageLoad = function() {
    parent.controller.setFrameSize();
}

DialogueEditor.prototype.onEditSentence = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "sentence";
        var table = "dialogue_sentences";
        var args = {
            dialogue: controller.dialogue_key,
        }
        window.parent.controller.editRecord(editor, table, record_id, args);
    }
}

DialogueEditor.prototype.onDeleteSentence = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this sentence?",
                                     controller.confirmDeleteSentence,
                                     {record: record_id});
}

DialogueEditor.prototype.confirmDeleteSentence = function(e) {
    window.parent.controller.hideWaiting();

    var table = controller.table_name;
    var record_id = e.data.record;
    service.deleteRecord(table, record, this.deleteSentenceSuccess);
}

DialogueEditor.prototype.deleteSentenceSuccess = function(data) {
    var record_id = data.record;
    $("#sentence-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}

DialogueEditor.prototype.queryFormSuccess = function(data) {
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "key") {
            var value = data[i].value;
            if (value) {
                controller.dialogue_key = value;
            }
            else {
                controller.dialogue_key = "";
            }
            break;
        }
    }

    CommonEditor.prototype.queryFormSuccess.call(this, data);
}

DialogueEditor.prototype.queryAreasSuccess = function(data) {
    controller.areas = data;
    controller.setFields();

    // Query sentences.
    service.queryDialogueSentences(controller.dialogue_key,
                                   controller.querySentenceTableSuccess,
                                   controller.failedCallback);

    // Query events.
    service.queryObjectEvents(controller.dialogue_key,
                              controller.queryEventTableSuccess,
                              controller.failedCallback);
}

DialogueEditor.prototype.querySentenceTableSuccess = function(data) {
    $("#sentence-table").bootstrapTable("destroy");
    $("#sentence-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: controller.parseFields(data.fields),
        data: utils.parseRows(data.fields, data.records),
        sortName: "ordinal",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}

DialogueEditor.prototype.queryEventTableSuccess = function(data) {
    var columns = controller.parseFields(data.fields);
    for (var i = 0; i < columns.length; i++) {
        if (columns[i].field == "trigger_obj" || columns[i].field == "trigger_type") {
            columns[i].hidden = true;
        }
    }

    $("#event-table").bootstrapTable("destroy");
    $("#event-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: columns,
        data: utils.parseRows(data.fields, data.records),
        sortName: "id",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}

DialogueEditor.prototype.addSentence = function(e) {
    if (!controller.dialogue_key) {
        window.parent.controller.notify("You should save this dialogue first.");
        return;
    }

    var editor = "sentence"
    var table = "dialogue_sentences";
    var record = "";
    var args = {
        dialogue: controller.dialogue_key,
    }
    window.parent.controller.editRecord(editor, table, record, args);
}

/*******************************************************
 * Events
 *******************************************************/
DialogueEditor.prototype.onAddEvent = function(e) {
    if (!controller.dialogue_key) {
        window.parent.controller.notify("You should save this dialogue first.");
        return;
    }

    var editor = "dialogue_event";
    var record = "";
    var args = {
        trigger: controller.dialogue_key,
    }
    window.parent.controller.editRecord(editor, controller.event_table, record, args);
}

DialogueEditor.prototype.onEditEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "dialogue_event";
        var args = {
            trigger: controller.dialogue_key,
        }
        window.parent.controller.editRecord(editor, controller.event_table, record_id, args);
    }
}

DialogueEditor.prototype.onDeleteEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteEvent,
                                     {record: record_id});
}

DialogueEditor.prototype.confirmDeleteEvent = function(e) {
    window.parent.controller.hideWaiting();

    var record_id = e.data.record;
    service.deleteRecord(controller.event_table, record_id, controller.deleteEventSuccess, controller.failedCallback);
}

DialogueEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}