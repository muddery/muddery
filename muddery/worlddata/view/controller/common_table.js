
controller = {
    init: function() {
        this.table_name = getQueryString("table");
        this.fields = [];
        this.rows = []

        this.bindEvents();

        service.queryTable(this.table_name, this.queryTableSuccess);
    },

    bindEvents: function() {
        $("#data_table").on("click", ".edit-row", this.onEdit);
        $("#data_table").on("click", ".delete-row", this.onDelete);
    },

    onEdit: function(e) {
        var index = $(e.currentTarget).attr("data-row-index");
        if (index) {
            index = parseInt(index);
            if (index >= 0 && index < controller.rows.length) {
                var table = controller.table_name;
                var record = controller.rows[index][0];
                window.parent.controller.editRecord(table, record);
            }
        }
    },

    onDelete: function(e) {
    },

    queryTableSuccess: function(data) {
        controller.setTable(data);
    },

    parseFields: function() {
        var cols = [{
            field: "operate",
            title: "Operate",
            formatter: this.operateButton,
        }];

        for (var i = 0; i < this.fields.length; i++) {
            cols.push({
                field: this.fields[i].name,
                title: this.fields[i].label,
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
            .attr("data-row-index", index)
            .text("Edit")
            .appendTo(block);

        var edit = $("<button>")
            .addClass("btn-link delete-row")
            .attr("type", "button")
            .attr("data-row-index", index)
            .text("Delete")
            .appendTo(block);

        return block.html();
    },

    parseRows: function() {
        var rows = [];
        for (var i = 0; i < this.rows.length; i++) {
            var row = {ID: i + 1};
            for (var j = 0; j < this.fields.length; j++) {
                row[this.fields[j]["name"]] = this.rows[i][j];
            }
            rows.push(row);
        }
        return rows;
    },
    
    setTable: function(table) {
        this.fields = table.fields;
        this.rows = table.rows;

        $("#data_table").bootstrapTable({
            cache: false,
            striped: true,
            pagination: true,
            pageList: [20, 50, 100],
            pageSize: 20,
            sidePagination: "client",
            columns: this.parseFields(),
            data: this.parseRows(),
            sortName: "id",
            sortOrder: "desc",
            clickToSelect: true,
            singleSelect: true,
        });

        window.parent.controller.setFrameSize();
    },

    loadData: function(data) {
        $("#data_table").bootstrapTable("load", data);
    }, 
}

$(document).ready(function() {
    controller.init();
});

