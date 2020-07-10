
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

    // Parse records to table rows.
    parseRows: function(fields, records) {
        var rows = [];
        for (var i = 0; i < records.length; i++) {
            var row = {ID: i + 1};
            for (var j = 0; j < fields.length; j++) {
                var field_name = fields[j]["name"];
                row[field_name] = records[i][j];
            }
            rows.push(row);
        }
        return rows;
    }
}
