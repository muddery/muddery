
/*
 * Derive from the base class.
 */
DialogueEditor = function() {
	CommonEditor.call(this);

    this.dialogue_key = "";
    this.sentence_fields = [];
}

DialogueEditor.prototype = prototype(CommonEditor.prototype);
DialogueEditor.prototype.constructor = DialogueEditor;


DialogueEditor.prototype.bindEvents = function() {
    CommonEditor.prototype.bindEvents.call(this);

    $("#add-sentence").on("click", this.addSentence);
    $("#sentence-table").on("click", ".edit-row", this.onEditSentence);
    $("#sentence-table").on("click", ".delete-row", this.onDeleteSentence);
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
    service.queryDialogueSentences(controller.dialogue_key, controller.querySentenceTableSuccess, controller.querySentenceTableFailed);
}

DialogueEditor.prototype.querySentenceTableSuccess = function(data) {
    controller.event_fields = data.fields;

    $("#sentence-table").bootstrapTable("destroy");
    $("#sentence-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: utils.parseFields(data.fields),
        data: utils.parseRows(data.fields, data.records),
        sortName: "ordinal",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}

DialogueEditor.prototype.querySentencesTableFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
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
