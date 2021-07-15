
/*
 * Derive from the base class.
 */
PropertiesDictTable = function() {
	CommonTable.call(this);

	this.table_name = "properties_dict";

	this.element = "";
}

PropertiesDictTable.prototype = prototype(CommonTable.prototype);
PropertiesDictTable.prototype.constructor = PropertiesDictTable;

PropertiesDictTable.prototype.init = function() {
    this.bindEvents();

    service.queryAllElements(this.queryAllElementsSuccess, this.queryTableFailed);
    service.queryElementProperties(this.element, this.queryTableSuccess);
}


/***********************************
 *
 * Events
 *
 ***********************************/
PropertiesDictTable.prototype.bindEvents = function() {
    CommonTable.prototype.bindEvents.call(this);

    $("#select-element").on("change", this.onSelectElementChange);
}

PropertiesDictTable.prototype.onSelectElementChange = function(e) {
    controller.element = $(this).val();

    service.queryElementProperties(controller.element, controller.refreshTableSuccess);
}

PropertiesDictTable.prototype.queryAllElementsSuccess = function(data) {
    var container = $("#select-element");
    container.children().remove();

    $("<option>")
            .attr("disabled", "disabled")
            .attr("selected", "selected")
            .text("请选择")
            .appendTo(container);

    // Build inheritance tree.
    for (var key in data) {
        var item = data[key];
        if (item.parent && item.parent in data) {
            var parent = data[item.parent];
            if (!("children" in parent)) {
                parent.children = [];
            }
            parent.children.push(key);
        }
    }

    var tree = [];
    for (var key in data) {
        // Find the root.
        if (!data[key].parent) {
            controller.setTreeLevel(data, tree, key, 0);
        }
    }

    for (var i = 0; i < tree.length; i++) {
        var prescript = new Array(tree[i].level + 1).join("&emsp;&emsp;");
        var name = prescript + tree[i].name + "(" + tree[i].key + ")";
        $("<option>")
            .attr("value", tree[i].key)
            .html(name)
            .appendTo(container);
    }
}

PropertiesDictTable.prototype.setTreeLevel = function(source, target, node, level) {
    var item = $.extend({}, source[node]);
    item.key = node;
    item.level = level;
    target.push(item);

    for (var n in source[node].children) {
        this.setTreeLevel(source, target, source[node].children[n], level + 1);
    }
}

PropertiesDictTable.prototype.refresh = function() {
    service.queryElementProperties(
        this.element,
        this.refreshTableSuccess,
        this.failedCallback
    );
}

PropertiesDictTable.prototype.onAdd = function(e) {
    window.parent.controller.editPropertiesDict(controller.element);
}

PropertiesDictTable.prototype.onEdit = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        window.parent.controller.editPropertiesDict(controller.element, record_id);
    }
}
