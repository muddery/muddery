
/*
 * Derive from the base class.
 */
PropertiesDictTable = function() {
	CommonTable.call(this);

	this.typeclass = "";
}

PropertiesDictTable.prototype = prototype(CommonTable.prototype);
PropertiesDictTable.prototype.constructor = PropertiesDictTable;

PropertiesDictTable.prototype.init = function() {
    this.bindEvents();

    service.queryAllTypeclasses(this.queryAllTypeclassesSuccess, this.queryTableFailed);
    service.queryTypeclassProperties(this.typeclass, this.queryTableSuccess);
}

/***********************************
 *
 * Events
 *
 ***********************************/
PropertiesDictTable.prototype.bindEvents = function() {
    CommonTable.prototype.bindEvents.call(this);

    $("#select-typeclass").on("change", this.onSelectTypeclassChange);
}

PropertiesDictTable.prototype.onSelectTypeclassChange = function(e) {
    controller.typeclass = $(this).val();

    service.queryTypeclassProperties(controller.typeclass, controller.refreshTableSuccess);
}

PropertiesDictTable.prototype.queryAllTypeclassesSuccess = function(data) {
    var container = $("#select-typeclass");
    container.children().remove();

    $("<option>")
            .attr("disabled", "disabled")
            .attr("selected", "selected")
            .text("请选择")
            .appendTo(container);

    for (var key in data) {
        $("<option>")
            .attr("value", key)
            .text(data[key].name)
            .appendTo(container);
    }
}

PropertiesDictTable.prototype.refresh = function() {
    service.queryTypeclassProperties(this.typeclass, this.refreshTableSuccess);
}

PropertiesDictTable.prototype.onAdd = function(e) {
    var typeclass = controller.typeclass;
    window.parent.controller.editObject(typeclass, "");
}

PropertiesDictTable.prototype.onEdit = function(e) {
    var object_key = $(this).attr("data-object-key");
    if (object_key) {
        var typeclass = controller.typeclass;
        window.parent.controller.editObject(typeclass, object_key);
    }
}

PropertiesDictTable.prototype.onDelete = function(e) {
    var object_key = $(this).attr("data-object-key");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete,
                                     {object_key: object_key});
}

PropertiesDictTable.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var object_key = e.data.object_key;
    var typeclass = controller.typeclass;
    controller.deleteObject(object_key, typeclass);
}

PropertiesDictTable.prototype.deleteObject = function(object_key, typeclass) {
    service.deleteObject(object_key, typeclass, this.deleteSuccess);
}

PropertiesDictTable.prototype.deleteSuccess = function(data) {
    var object_key = data.obj_key;
    $("#data-table").bootstrapTable("remove", {
        field: "key",
        values: [object_key]
    });
}

// Set table buttons, use object's key as the row's key.
PropertiesDictTable.prototype.operateButton = function(value, row, index) {
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

PropertiesDictTable.prototype.queryPropertiesSuccess = function(data) {
}