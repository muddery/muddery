
/*
 * callback_success: function(data)
 * callback_error: function(code, message, data)
 */
service = {
    onSuccess: function(callback_success, callback_error) {
        var func = function(data) {
            if (!data) {
	            data = {
                    code: -1,
                    msg: "Empty result.",
                };
            }
            else if (!("code" in data) || !("data" in data)) {
                data = {
                    code: -1,
                    msg: "Wrong result format.",
                };
            }
            
            if (data.code != 0) {
	            console.warn("Return error: " + data.code + "：" + data.msg);
	            if (callback_error) {
		            callback_error(data.code, data.msg, data.data);
	            }
            }
            else {
	            if (callback_success) {
		            callback_success(data.data);
	            }
            }
        }

        return func;
    },

    onError: function(callback_error) {
        var func = function(request, status) {
            if (callback_error) {
                callback_error(-2, request.statusText, request.status);
            }
        }

        return func;
    },

    sendRequest: function(path, func_no, args, callback_success, callback_error) {
	    var url = CONFIG.api_url + path;
	    params = {
            func: func_no,
            args: args,
        };

	    $.ajax({
            url: url,
		    type: "POST",
            contentType: "application/json",
		    cache: false,
		    data: JSON.stringify(params),
		    dataType: "json",
		    success: this.onSuccess(callback_success, callback_error),
		    error: this.onError(callback_error),
	    });
    },

    sendFile: function(path, func_no, file_obj, args, callback_success, callback_error) {
	    var url = CONFIG.api_url + path;

        var form_file = new FormData();
        form_file.append("func", func_no);
        form_file.append("args", JSON.stringify(args));
        form_file.append("file", file_obj);

        $.ajax({
            url: url,
            type: "POST",
            contentType: false,
            cache: false,
            data: form_file,
            dataType: "json",
            processData: false,
		    success: this.onSuccess(callback_success, callback_error),
		    error: this.onError(callback_error),
        });
    },

    downloadFile: function(path, func_no, args) {
        var url = CONFIG.api_url + path;

        var form = $("<form></form>")
            .attr("action", url)
            .attr("method", "POST");

        $("<input>")
            .attr("name", "func_no")
            .attr("value", func_no)
            .appendTo(form);
        
        var args = JSON.stringify(args);
        $("<input>")
            .attr("name", "args")
            .attr("value", args)
            .appendTo(form);

        form.appendTo('body').submit().remove();
    },

    login: function(username, password, callback_success, callback_error) {
        var args = {
            username: username,
            password: password,
        };
        this.sendRequest("login", "", args, callback_success, callback_error);
    },

    logout: function(callback_success, callback_error) {
        this.sendRequest("logout", "", {}, callback_success, callback_error);
    },

    queryFields: function(table_name, callback_success, callback_error) {
        var args = {
            table: table_name,
        };
        this.sendRequest("query_fields", "", args, callback_success, callback_error);
    },

    queryTable: function(table_name, callback_success, callback_error) {
        var args = {
            table: table_name,
        };
        this.sendRequest("query_table", "", args, callback_success, callback_error);
    },

    queryRecord: function(table_name, record_id, callback_success, callback_error) {
        var args = {
            table: table_name,
            record: record_id,
        };
        this.sendRequest("query_record", "", args, callback_success, callback_error);
    },

    queryForm: function(table_name, record_id, callback_success, callback_error) {
        var args = {
            table: table_name,
            record: record_id,
        };
        this.sendRequest("query_form", "", args, callback_success, callback_error);
    },

    queryAreas: function(callback_success, callback_error) {
        this.sendRequest("query_areas", "", {}, callback_success, callback_error);
    },

    /*  Query an event's additional data's form.
     *  Args:
     *      type: (string) event's type.
     *      event: （string) event's key.
     */
    queryEventDataForm: function(type, event, callback_success, callback_error) {
        var args = {
            type: type,
            event: event,
        };
        this.sendRequest("query_event_data_form", "", args, callback_success, callback_error);
    },

    saveForm: function(values, table_name, record_id, callback_success, callback_error) {
        var args = {
            values: values,
            table: table_name,
            record: record_id,
        };
        this.sendRequest("save_form", "", args, callback_success, callback_error);
    },

    deleteRecord: function(table_name, record_id, callback_success, callback_error) {
        var args = {
            table: table_name,
            record: record_id,
        };
        this.sendRequest("delete_record", "", args, callback_success, callback_error);
    },

    queryTables: function(callback_success, callback_error) {
        this.sendRequest("query_tables", "", {}, callback_success, callback_error);
    },

    uploadDataZip: function(file_obj, callback_success, callback_error) {
        this.sendFile("upload_zip", "", file_obj, {}, callback_success, callback_error);
    },

    uploadResourceZip: function(file_obj, callback_success, callback_error) {
        this.sendFile("upload_resources", "", file_obj, {}, callback_success, callback_error);
    },

    uploadSingleData: function(file_obj, table_name, callback_success, callback_error) {
        var args = {
            table: table_name,
        };
        this.sendFile("upload_single_data", "", file_obj, args, callback_success, callback_error);
    },

    uploadImage: function(file_obj, field_name, file_type, callback_success, callback_error) {
        var args = {
            field: field_name,
            type: file_type,
        };
        this.sendFile("upload_image", "", file_obj, args, callback_success, callback_error);
    },

    queryDataFileTypes: function(callback_success, callback_error) {
        this.sendRequest("query_data_file_types", "", {}, callback_success, callback_error);
    },

    downloadDataZip: function(file_type) {
        var args = {
            type: file_type,
        };
        this.downloadFile("download_zip", "", args);
    },

    downloadResourceZip: function() {
        this.downloadFile("download_resources", "", {});
    },

    downloadSingleData: function(table_name, file_type) {
        var args = {
            table: table_name,
            type: file_type,
        };
        this.downloadFile("download_single_data", "", args);
    },

    applyChanges: function(callback_success, callback_error) {
        this.sendRequest("apply_changes", "", {}, callback_success, callback_error);
    },
}


