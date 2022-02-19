
/*
 * Derive from the base class.
 */
MatterTable = function() {
	ElementTable.call(this);
}

MatterTable.prototype = prototype(ElementTable.prototype);
MatterTable.prototype.constructor = MatterTable;

MatterTable.prototype.onAdd = function(e) {
    var element_type = controller.element_type;
    window.parent.controller.editMatter(element_type, "");
}

MatterTable.prototype.onEdit = function(e) {
    var element_key = $(this).attr("data-element-key");
    if (element_key) {
        var element_type = controller.element_type;
        window.parent.controller.editMatter(element_type, element_key);
    }
}
