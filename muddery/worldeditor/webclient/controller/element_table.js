
/*
 * Derive from the base class.
 */
ElementTable = function() {
	CommonTable.call(this);
}

ElementTable.prototype = prototype(CommonTable.prototype);
ElementTable.prototype.constructor = ElementTable;

ElementTable.prototype.init = function() {
    this.element_type = utils.getQueryString("element_type");

    $("#table-name").text(this.element_type);
    this.bindEvents();

    service.queryElementTable(this.element_type, this.queryTableSuccess, this.queryTableFailed);
}

ElementTable.prototype.refresh = function() {
    service.queryElementTable(this.element_type, this.refreshTableSuccess);
}

ElementTable.prototype.onAdd = function(e) {
    var element_type = controller.element_type;
    window.parent.controller.editElement(element_type, element_type, "");
}

ElementTable.prototype.onEdit = function(e) {
    var element_key = $(this).attr("data-element-key");
    if (element_key) {
        var base_element_type = controller.element_type;
        var element_type = $(this).attr("data-element-type") || base_element_type;
        window.parent.controller.editElement(base_element_type, element_type, element_key);
    }
}

ElementTable.prototype.onDelete = function(e) {
    var element_key = $(this).attr("data-element-key");
    window.parent.controller.confirm(
        "",
        "Delete this record?",
        controller.confirmDelete,
        {element_key: element_key},
    );
}

ElementTable.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var element_key = e.data.element_key;
    var element_type = controller.element_type;
    controller.deleteElement(element_key, element_type);
}

ElementTable.prototype.deleteElement = function(element_key, element_type) {
    service.deleteElement(element_key, element_type, this.deleteSuccess, this.deleteFailed);
}

ElementTable.prototype.deleteSuccess = function(data) {
    var element_key = data.element_key;
    $("#data-table").bootstrapTable("remove", {
        field: "key",
        values: [element_key]
    });
}

// Set table buttons, use the element's key as the row's key.
ElementTable.prototype.operateButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-element-key", row["key"])
        .attr("data-element-type", row["element_type"])
        .text("Edit")
        .appendTo(block);

    var del = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-element-key", row["key"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}
