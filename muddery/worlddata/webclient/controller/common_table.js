
controller = {
    field_length: 20,

    init: function() {
        this.editor_type = utils.getQueryString("editor");
        this.table_name = utils.getQueryString("table");
        this.fields = [];

        $("#table-name").text(this.table_name);

        this.bindEvents();

        service.queryTable(this.table_name, this.queryTableSuccess, this.queryTableFailed);
    },

    bindEvents: function() {
        $("#add-record").on("click", this.onAddRecord);
        $("#data-table").on("click", ".edit-row", this.onEdit);
        $("#data-table").on("click", ".delete-row", this.onDelete);
    },

    onAddRecord: function(e) {
        var editor = controller.editor_type;
        var table = controller.table_name;
        window.parent.controller.editRecord(editor, table);
    },

    onEdit: function(e) {
        var record_id = $(this).attr("data-record-id");
        if (record_id) {
            var editor = controller.editor_type;
            var table = controller.table_name;
            window.parent.controller.editRecord(editor, table, record_id);
        }
    },

    onDelete: function(e) {
        var record_id = $(this).attr("data-record-id");
        window.parent.controller.confirm("",
                                         "Delete this record?",
                                         controller.confirmDelete,
                                         {record: record_id});
    },

    refresh: function() {
        service.queryTable(this.table_name, this.refreshTableSuccess);
    },

    queryTableSuccess: function(data) {
        controller.fields = data.fields;

        $("#data-table").bootstrapTable({
            cache: false,
            striped: true,
            pagination: true,
            pageList: [20, 50, 100],
            pageSize: 20,
            sidePagination: "client",
            columns: utils.parseFields(data.fields),
            data: utils.parseRows(data.fields, data.records, controller.field_length),
            sortName: "id",
            sortOrder: "asc",
            clickToSelect: true,
            singleSelect: true,
        });

        window.parent.controller.setFrameSize();
    },

    queryTableFailed: function() {
        window.parent.controller.notify("ERROR", code + ": " + message);
    },

    refreshTableSuccess: function(data) {
        $("#data-table").bootstrapTable("load", utils.parseRows(data.fields, data.records, controller.field_length));

        window.parent.controller.setFrameSize();
    },

    loadData: function(data) {
        $("#data-table").bootstrapTable("load", data);
    },

    confirmDelete: function(e) {
        window.parent.controller.hide_waiting();

        var table = controller.table_name;
        var record_id = e.data.record;
        controller.deleteRecord(table, record_id);
    },

    deleteRecord: function(table, record) {
        service.deleteRecord(table, record, this.deleteSuccess);
    },

    deleteSuccess: function(data) {
        var record_id = data.record;
        $("#data-table").bootstrapTable("remove", {
            field: "id",
            values: [record_id],
        });
    },
}

$(document).ready(function() {
    controller.init();
});

