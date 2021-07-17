
/*
 * Derive from the base class.
 */
ObjectTable = function() {
	CommonTable.call(this);
}

ObjectTable.prototype = prototype(CommonTable.prototype);
ObjectTable.prototype.constructor = ObjectTable;

ObjectTable.prototype.init = function() {
    this.element_type = utils.getQueryString("element_type");

    $("#table-name").text(this.element_type);
    this.bindEvents();

    service.queryElementTable(this.element_type, this.queryTableSuccess, this.queryTableFailed);
}

ObjectTable.prototype.refresh = function() {
    service.queryElementTable(this.element_type, this.refreshTableSuccess);
}

ObjectTable.prototype.onAdd = function(e) {
    var element_type = controller.element_type;
    window.parent.controller.editObject(element_type, "");
}

ObjectTable.prototype.onEdit = function(e) {
    var object_key = $(this).attr("data-object-key");
    if (object_key) {
        var element_type = controller.element_type;
        window.parent.controller.editObject(element_type, object_key);
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

    var object_key = e.data.object_key;
    var element_type = controller.element_type;
    controller.deleteObject(object_key, element_type);
}

ObjectTable.prototype.deleteObject = function(object_key, element_type) {
    service.deleteObject(object_key, element_type, this.deleteSuccess);
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
