
controller = {
    init: function() {
        this.table_name = getQueryString("table");
        this.fields = [];

        $("#table-name").text(this.table_name);

        this.bindEvents();

        service.queryTable(this.table_name, this.queryTableSuccess);
    },

    bindEvents: function() {
        $("#add-record").on("click", this.onAddRecord);
        $("#data-table").on("click", ".edit-row", this.onEdit);
        $("#data-table").on("click", ".delete-row", this.onDelete);
    },

    onAddRecord: function(e) {
        var table = controller.table_name;
        window.parent.controller.editRecord(table);
    },

    onEdit: function(e) {
        var record_id = $(this).attr("data-record-id");
        if (record_id) {
            var table = controller.table_name;
            window.parent.controller.editRecord(table, record_id);
        }
    },

    onDelete: function(e) {
        var record_id = $(this).attr("data-record-id");
        window.parent.controller.confirm("",
                                         "Delete this record?",
                                         controller.confirmDelete,
                                         {record: record_id});
    },

    queryTableSuccess: function(data) {
        controller.setTable(data);
    },

    parseFields: function(fields) {
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
    },

    operateButton: function(value, row, index) {
        var block = $("<div>");

        var content = $("<div>")
            .addClass("btn-group")
            .appendTo(block);

        var edit = $("<button>")
            .addClass("btn-link edit-row")
            .attr("type", "button")
            .attr("data-record-id", row["id"])
            .text("Edit")
            .appendTo(block);

        var edit = $("<button>")
            .addClass("btn-link delete-row")
            .attr("type", "button")
            .attr("data-record-id", row["id"])
            .text("Delete")
            .appendTo(block);

        return block.html();
    },

    parseRows: function(fields, records) {
        var rows = [];
        for (var i = 0; i < records.length; i++) {
            var row = {ID: i + 1};
            for (var j = 0; j < fields.length; j++) {
                row[fields[j]["name"]] = records[i][j];
            }
            rows.push(row);
        }
        return rows;
    },
    
    setTable: function(table) {
        this.fields = table.fields;

        $("#data-table").bootstrapTable({
            cache: false,
            striped: true,
            pagination: true,
            pageList: [20, 50, 100],
            pageSize: 20,
            sidePagination: "client",
            columns: this.parseFields(table.fields),
            data: this.parseRows(table.fields, table.records),
            sortName: "id",
            sortOrder: "asc",
            clickToSelect: true,
            singleSelect: true,
        });

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

