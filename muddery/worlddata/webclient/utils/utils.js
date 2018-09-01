
utils = {
    getQueryString: function(name) {
        var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
        var args = window.location.search.substr(1);
        if (args.substr(-1) == "/") {
            args = args.substr(0, args.length - 1);
        }

        var r = args.match(reg);
        if (r != null) {
            return unescape(r[2]);
        }
        return null;
    },

    // Parse fields data to table headers.
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

    // Set table buttons.
    operateButton: function(value, row, index) {
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
    },

    // Parse records to table rows.
    parseRows: function(fields, records, max_length) {
        var rows = [];
        for (var i = 0; i < records.length; i++) {
            var row = {ID: i + 1};
            for (var j = 0; j < fields.length; j++) {
                var value = records[i][j];
                if (value.length > max_length) {
                    value = value.slice(0, max_length + 1) + "...";
                }
                row[fields[j]["name"]] = value;
            }
            rows.push(row);
        }
        return rows;
    },
}
