
controller = {
    init: function() {
        this.bindEvents();

        service.queryTables(this.queryTablesSuccess);
        service.queryDataFileTypes(this.queryFileTypesSuccess);

        window.parent.controller.setFrameSize();
    },

    bindEvents: function() {
        $(".btn-browse").on("click", this.onBrowse);
        $(".file-input").on("change", this.onFileChanged);
        $(".btn-download").on("click", this.onDownload);
        $(".btn-upload").on("click", this.onUpload);
    },

    onBrowse: function(e) {
        $(this).parent().find(".file-input").click();
    },

    onFileChanged: function(e) {
        var filepath = $(this).val();
        $(this).parent().find(".file-text").val(filepath);  
    },

    onUpload: function(e) {
        var group = $(this).parent();
        var file_input = group.find(".file-input");
        if (file_input.length < 1) {
            return;
        }

        var file_obj = file_input[0].files[0];
        if (typeof (file_obj) == "undefined" || file_obj.size <= 0) {
            return;
        }

        if (group.attr("id") == "upload-zip") {
            service.uploadDataZip(file_obj, controller.uploadSuccess, controller.uploadFailed);
        }
        else if (group.attr("id") == "upload-resource") {
            service.uploadResourceZip(file_obj, controller.uploadSuccess, controller.uploadFailed);
        }
        else if (group.attr("id") == "upload-file") {
            var table_name = group.find(".table-select").val();
            service.uploadSingleData(file_obj, table_name, controller.uploadSuccess, controller.uploadFailed);
        }

        window.parent.controller.show_waiting("", "Uploading...");
    },

    onDownload: function(e) {
        var group = $(this).parent();

        if (group.attr("id") == "download-zip") {
            var file_type = group.find(".file-type-select").val();
            service.downloadDataZip(file_type);
        }
        else if (group.attr("id") == "download-resource") {
            service.downloadResourceZip();
        }
        else if (group.attr("id") == "download-file") {
            var table_name = group.find(".table-select").val();
            var file_type = group.find(".file-type-select").val();
            service.downloadSingleData(table_name, file_type);
        }
    },

    uploadSuccess: function(data) {
        window.parent.controller.notify("", "Upload success.");
    },

    uploadFailed: function(code, message, data) {
        window.parent.controller.notify("ERROR", code + ": " + message);
    },

    queryTablesSuccess: function(data) {
        var select = $("#download-table-names");
        select.empty();

        for (var i = 0; i < data.length; i++) {
            $("<option>")
                .attr("value", data[i]["key"])
                .text(data[i]["name"])
                .appendTo(select);
        }

        var select = $("#upload-table-names");
        select.empty();

        $("<option>")
            .attr("value", "")
            .text("---------")
            .appendTo(select);

        for (var i = 0; i < data.length; i++) {
            $("<option>")
                .attr("value", data[i]["key"])
                .text(data[i]["name"])
                .appendTo(select);
        }

        window.parent.controller.setFrameSize();
    },

    queryFileTypesSuccess: function(data) {
        var select = $(".file-type-select");
        select.empty();

        for (var i = 0; i < data.length; i++) {
            $("<option>")
                .attr("value", data[i]["type"])
                .text(data[i]["name"])
                .appendTo(select);
        }

        window.parent.controller.setFrameSize();
    },
}

$(document).ready(function() {
    controller.init();
});

