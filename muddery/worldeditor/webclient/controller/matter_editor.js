
/*
 * Derive from the base class.
 */
MatterEditor = function() {
	ElementEditor.call(this);

    this.conditional_desc_table = "conditional_desc";
}

MatterEditor.prototype = prototype(ElementEditor.prototype);
MatterEditor.prototype.constructor = MatterEditor;

MatterEditor.prototype.init = function() {
    ElementEditor.prototype.init.call(this);
}


/***********************************
 *
 * Conditional descriptions
 *
 ***********************************/
MatterEditor.prototype.bindEvents = function() {
    ElementEditor.prototype.bindEvents.call(this);

    $("#add-conditional-desc").on("click", this.onAddConditionalDesc);
    $("#conditional-desc-table").on("click", ".edit-row", this.onEditConditionalDesc);
    $("#conditional-desc-table").on("click", ".delete-row", this.onDeleteConditionalDesc);
}

MatterEditor.prototype.onAddConditionalDesc = function(e) {
    if (!controller.element_key) {
        window.parent.controller.notify("You should save this element first.");
        return;
    }

    window.parent.controller.editConditionalDesc(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        null
    );
}

MatterEditor.prototype.onEditConditionalDesc = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.editConditionalDesc(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        record_id
    );
}

MatterEditor.prototype.onDeleteConditionalDesc = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm(
        "",
        "Delete this description?",
        controller.confirmDeleteConditionalDesc,
        {record: record_id}
    );
}

MatterEditor.prototype.confirmDeleteConditionalDesc = function(e) {
    window.parent.controller.hideWaiting();

    var record_id = parseInt(e.data.record);
    service.deleteRecord(
        controller.conditional_desc_table,
        record_id,
        controller.deleteConditionalDescSuccess,
        controller.failedCallback
    );
}

MatterEditor.prototype.deleteConditionalDescSuccess = function(data) {
    var record_id = data.record;
    $("#conditional-desc-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}

MatterEditor.prototype.queryFormSuccess = function(data) {
    ElementEditor.prototype.queryFormSuccess.call(this, data);

    // Query conditional descriptions.
    service.queryConditionalDesc(
        controller.obj_element_type? controller.obj_element_type: controller.base_element_type,
        controller.element_key,
        controller.queryConditionalDescSuccess,
        controller.failedCallback
    );
}

MatterEditor.prototype.queryConditionalDescSuccess = function(data) {
    $("#conditional-desc-table").bootstrapTable("destroy");
    $("#conditional-desc-table").bootstrapTable({
        cache: false,
        striped: true,
        pagination: true,
        pageList: [20, 50, 100],
        pageSize: 20,
        sidePagination: "client",
        columns: controller.parseFields(data.fields),
        data: utils.parseRows(data.fields, data.records),
        sortName: "id",
        sortOrder: "asc",
        clickToSelect: true,
        singleSelect: true,
    });

    window.parent.controller.setFrameSize();
}
