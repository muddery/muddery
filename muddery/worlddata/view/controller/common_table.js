
controller = {
    init: function() {
        this.table_name = getQueryString("table");
        this.api = window.location.protocol + "//" + window.location.host + "/worlddata/editor/api/";
        this.columns = [];
        this.rows = [];

        service.queryColumns(this.table_name, this.queryColumnsSuccess);
    },

    queryColumnsSuccess: function(data) {
        controller.columns = data;
        service.queryTable(this.table_name, this.queryTableSuccess);
    },

    queryTableSuccess: function(data) {
        controller.rows = data;
        controller.createTable();
    },

    parseColumns: function(data) {
        var cols = [];
        for (var i = 0; i < data.length; i++) {
            cols.push({
                field: data[i][0],
                title: data[i][1],
                sortable: true,
            });
        }

        cols.push({
            field: "operate",
            title: "Operate",
            formatter: this.operateButton,
        });

        return cols;
    },

    operateButton: function() {
        return '\
<div class="btn-group">\
    <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">Operate\
        <span class="caret"></span>\
    </button>\
    <ul class="dropdown-menu row-operate" role="menu">\
        <li><a href="#">Edit</a></li>\
        <li><a href="#">Delete</a></li>\
    </ul>\
</div>';
    },

    parseRows: function(data) {
        var rows = [];
        for (var i = 0; i < data.length; i++) {
            var row = {ID: i + 1};
            for (var j = 0; j < this.columns.length; j++) {
                row[this.columns[j][0]] = data[i][j];
            }
            rows.push(row);
        }
        return rows;
    },
    
    createTable: function() {
        $("#data_table").bootstrapTable({
            cache: false,
            striped: true,
            pagination: true,
            pageList: [20, 50, 100],
            pageSize: 20,
            sidePagination: "client",
            columns: this.parseColumns(this.columns),
            data: this.parseRows(this.rows),
            sortName: "id",
            sortOrder: "desc",
            clickToSelect: true,
            singleSelect: true,
        });
    },

    loadData: function(data) {
        $("#data_table").bootstrapTable("load", data);
    },
}

$(document).ready(function() {
    controller.init();
});

