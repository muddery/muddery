
/*
 * Derive from the base class.
 */
PropertiesDictTable = function() {
	CommonTable.call(this);

	this.table_name = "properties_dict";

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
            .text(data[key].name + "(" + key + ")")
            .appendTo(container);
    }
}

PropertiesDictTable.prototype.refresh = function() {
    service.queryTypeclassProperties(this.typeclass, this.refreshTableSuccess);
}

PropertiesDictTable.prototype.onAdd = function(e) {
    window.parent.controller.editPropertiesDict(controller.typeclass);
}

PropertiesDictTable.prototype.onEdit = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        window.parent.controller.editPropertiesDict(controller.typeclass, record_id);
    }
}
