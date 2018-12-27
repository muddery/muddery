
/*
 * Get the prototype of the base class.
 */
prototype = function(base, el) {
    var Base = function(){};
    Base.prototype = base;
    return new Base(el);
}

////////////////////////////////////////
//
// The base of view controllers.
//
////////////////////////////////////////

/*
 * The base controller's constructor.
 */
CommonTable = function() {
    this.field_length = 20;
    this.fields = [];
}

CommonTable.prototype.init = function() {
    this.editor_type = utils.getQueryString("editor");
    this.table_name = utils.getQueryString("table");

    $("#table-name").text(this.table_name);

    this.bindEvents();

    service.queryTable(this.table_name, this.queryTableSuccess, this.queryTableFailed);
}

CommonTable.prototype.bindEvents = function() {
    $("#add-record").on("click", this.onAddRecord);
    $("#data-table").on("click", ".edit-row", this.onEdit);
    $("#data-table").on("click", ".delete-row", this.onDelete);
}

CommonTable.prototype.onAddRecord = function(e) {
    var editor = controller.editor_type;
    var table = controller.table_name;
    window.parent.controller.editRecord(editor, table);
}

CommonTable.prototype.onEdit = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = controller.editor_type;
        var table = controller.table_name;
        window.parent.controller.editRecord(editor, table, record_id);
    }
}

CommonTable.prototype.onDelete = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDelete,
                                     {record: record_id});
}

CommonTable.prototype.refresh = function() {
    service.queryTable(this.table_name, this.refreshTableSuccess);
}

CommonTable.prototype.queryTableSuccess = function(data) {
    controller.fields = data.fields;

    $("#data-table").bootstrapTable({
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

// Parse fields data to table headers.
CommonTable.prototype.parseFields = function(fields) {
    var cols = [{
        field: "operate",
        title: "Operate",
        formatter: this.operateButton,
    }];

    for (var i = 0; i < fields.length; i++) {
        cols.push({
            field: fields[i].name,
            title: fields[i].label,
            sortable: true,
        });
    }

    return cols;
}

// Set table buttons.
CommonTable.prototype.operateButton = function(value, row, index) {
    var block = $("<div>");

    var content = $("<div>")
        .addClass("btn-group")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs edit-row")
        .attr("type", "button")
        .attr("data-record-id", row["id"])
        .text("Edit")
        .appendTo(block);

    var edit = $("<button>")
        .addClass("btn-xs btn-danger delete-row")
        .attr("type", "button")
        .attr("data-record-id", row["id"])
        .text("Delete")
        .appendTo(block);

    return block.html();
}

CommonTable.prototype.queryTableFailed = function(code, message) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

CommonTable.prototype.refreshTableSuccess = function(data) {
    $("#data-table").bootstrapTable("load", utils.parseRows(data.fields, data.records));

    window.parent.controller.setFrameSize();
}

CommonTable.prototype.loadData = function(data) {
    $("#data-table").bootstrapTable("load", data);
}

CommonTable.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var table = controller.table_name;
    var record_id = e.data.record;
    controller.deleteRecord(table, record_id);
}

CommonTable.prototype.deleteRecord = function(table, record) {
    service.deleteRecord(table, record, this.deleteSuccess);
}

CommonTable.prototype.deleteSuccess = function(data) {
    var record_id = data.record;
    $("#data-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}
