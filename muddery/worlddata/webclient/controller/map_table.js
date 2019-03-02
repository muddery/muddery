
/*
 * Derive from the base class.
 */
MapTable = function() {
	CommonTable.call(this);
}

MapTable.prototype = prototype(CommonTable.prototype);
MapTable.prototype.constructor = MapTable;

MapTable.prototype.init = function() {
    this.typeclass = "AREA";

    this.bindEvents();

    service.queryTypeclassTable(this.typeclass, this.queryTableSuccess, this.queryTableFailed);
}

MapTable.prototype.refresh = function() {
    service.queryTypeclassTable(this.typeclass, this.refreshTableSuccess);
}

MapTable.prototype.onAdd = function(e) {
    window.parent.controller.editMap();
}

MapTable.prototype.onEdit = function(e) {
    var map_key = $(this).attr("data-map-key");
    if (map_key) {
        window.parent.controller.editMap(map_key);
    }
}

MapTable.prototype.onDelete = function(e) {
    var map_key = $(this).attr("data-map-key");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete,
                                     {map_key: map_key});
}

MapTable.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var map_key = e.data.map_key;
    controller.deleteMap(map_key);
}

MapTable.prototype.deleteMap = function(map_key) {
    service.deleteMap(map_key, this.deleteSuccess);
}

MapTable.prototype.deleteSuccess = function(data) {
    var map_key = data.map_key;
    $("#data-table").bootstrapTable("remove", {
        field: "key",
        values: [map_key]
    });
}

// Set table buttons, use object's key as the row's key.
MapTable.prototype.operateButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-map-key", row["key"])
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-map-key", row["key"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}
