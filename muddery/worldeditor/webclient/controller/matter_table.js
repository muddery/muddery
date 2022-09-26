
/*
 * Derive from the base class.
 */
MatterTable = function() {
	ElementTable.call(this);
}

MatterTable.prototype = prototype(ElementTable.prototype);
MatterTable.prototype.constructor = MatterTable;

MatterTable.prototype.onAdd = function(e) {
    var base_element_type = controller.element_type;
    window.parent.controller.editMatter(base_element_type, base_element_type, "");
}

MatterTable.prototype.onEdit = function(e) {
    var element_key = $(this).attr("data-element-key");
    if (element_key) {
        var base_element_type = controller.element_type;
        var element_type = $(this).attr("data-element-type") || base_element_type;
        window.parent.controller.editMatter(base_element_type, element_type, element_key);
    }
}
