
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
    service.queryTypeclassProperties(this.typeclass,
                                     this.refreshTableSuccess,
                                     this.failedCallback);
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
