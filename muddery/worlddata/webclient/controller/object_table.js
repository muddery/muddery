
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
    var typeclass = controller.typeclass;
    window.parent.controller.editObject(typeclass, "");
}

ObjectTable.prototype.onEdit = function(e) {
    var object_key = $(this).attr("data-object-key");
    if (object_key) {
        var typeclass = controller.typeclass;
        window.parent.controller.editObject(typeclass, object_key);
    }
}

ObjectTable.prototype.onDelete = function(e) {
    var object_key = $(this).attr("data-object-key");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete,
                                     {object_key: object_key});
}

ObjectTable.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var typeclass = controller.typeclass;
    var object_key = e.data.object_key;
    controller.deleteObject(typeclass, object_key);
}

ObjectTable.prototype.deleteObject = function(typeclass, object_key) {
    service.deleteObject(typeclass, object_key, this.deleteSuccess);
}

ObjectTable.prototype.deleteSuccess = function(data) {
    var object_key = data.obj_key;
    $("#data-table").bootstrapTable("remove", {
        field: "key",
        values: [object_key]
    });
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
