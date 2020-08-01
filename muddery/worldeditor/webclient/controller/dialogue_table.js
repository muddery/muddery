
/*
 * Derive from the base class.
 */
DialogueTable = function() {
	CommonTable.call(this);
}

DialogueTable.prototype = prototype(CommonTable.prototype);
DialogueTable.prototype.constructor = DialogueTable;

DialogueTable.prototype.init = function() {
    this.editor_type = utils.getQueryString("editor");
    this.table_name = "dialogues";

    $("#table-name").text(this.table_name);

    this.bindEvents();

    service.queryDialoguesTable(this.queryTableSuccess, this.queryTableFailed);
}

DialogueTable.prototype.refresh = function() {
    service.queryDialoguesTable(this.refreshTableSuccess);
}