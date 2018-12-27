
/*
 * Derive from the base class.
 */
ObjectTable = function() {
	CommonTable.call(this);
}

ObjectTable.prototype = prototype(CommonTable.prototype);
ObjectTable.prototype.constructor = ObjectTable;

ObjectTable.prototype.init = function() {
    this.typeclass = utils.getQueryString("typeclass");

    $("#table-name").text(this.typeclass);
    this.bindEvents();

    service.queryTypeclassTable(this.typeclass, this.queryTableSuccess, this.queryTableFailed);
}

ObjectTable.prototype.refresh = function() {
    service.queryTypeclassTable(this.typeclass, this.refreshTableSuccess);
}

ObjectTable.prototype.onAddRecord = function(e) {
    var editor = "object";
    var typeclass = controller.typeclass;
    window.parent.controller.editObject(editor, typeclass, "");
}

ObjectTable.prototype.onEdit = function(e) {
    var object_key = $(this).attr("data-object-key");
    if (object_key) {
        var editor = "object";
        var typeclass = controller.typeclass;
        window.parent.controller.editObject(editor, typeclass, object_key);
    }
}

// Set table buttons, use object's key as the row's key.
ObjectTable.prototype.operateButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-object-key", row["key"])
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-object-key", row["key"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}
