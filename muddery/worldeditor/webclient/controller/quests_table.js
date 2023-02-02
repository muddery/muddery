
/*
 * Derive from the base class.
 */
QuestsTable = function() {
	ElementTable.call(this);
}

QuestsTable.prototype = prototype(ElementTable.prototype);
QuestsTable.prototype.constructor = QuestsTable;

QuestsTable.prototype.onAdd = function(e) {
    var base_element_type = controller.element_type;
    window.parent.controller.editQuest("");
}

QuestsTable.prototype.onEdit = function(e) {
    var element_key = $(this).attr("data-element-key");
    if (element_key) {
        var base_element_type = controller.element_type;
        var element_type = $(this).attr("data-element-type") || base_element_type;
        window.parent.controller.editQuest(element_key);
    }
}
