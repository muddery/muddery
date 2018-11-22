
/*
 * Derive from the base class.
 */
ObjectTable = function() {
	CommonTable.call(this);
}

ObjectTable.prototype = prototype(CommonTable.prototype);
ObjectTable.prototype.constructor = ObjectEditor;

ObjectTable.prototype.onAddRecord = function(e) {
    var editor = "object";
    var table = controller.table_name;
    window.parent.controller.editRecord(editor, typeclass);
}

ObjectTable.prototype.onEdit = function(e) {
    var object_key = $(this).attr("data-object-key");
    if (object_key) {
        var editor = "object";
        var table = controller.table_name;
        window.parent.controller.editObject(editor, typeclass, object_key);
    }
}
