
/*
 * callback_success: function(data, context)
 * callback_failed: function(code, message, data, context)
 */
service = {
    onSuccess: function(callback_success, callback_failed) {
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
	            if (callback_failed) {
		            callback_failed(data.code, data.msg, data.data, this);
	            }
            }
            else {
	            if (callback_success) {
		            callback_success(data.data, this);
	            }
            }
        }

        return func;
    },

    onError: function(callback_failed) {
        var func = function(request, status) {
            if (callback_failed) {
                callback_failed(-2, request.statusText, request.status, this);
            }
        }

        return func;
    },

    sendRequest: function(path, func_no, args, callback_success, callback_failed, context) {
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
            context: context,
		    data: JSON.stringify(params),
		    dataType: "json",
		    success: this.onSuccess(callback_success, callback_failed),
		    error: this.onError(callback_failed)
	    });
    },

    sendFile: function(path, func_no, file_obj, args, callback_success, callback_failed, context) {
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
            context: context,
            data: form_file,
            dataType: "json",
            processData: false,
		    success: this.onSuccess(callback_success, callback_failed),
		    error: this.onError(callback_failed)
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

    login: function(username, password, callback_success, callback_failed, context) {
        var args = {
            username: username,
            password: password
        };
        this.sendRequest("login", "", args, callback_success, callback_failed, context);
    },

    logout: function(callback_success, callback_failed, context) {
        this.sendRequest("logout", "", {}, callback_success, callback_failed, context);
    },

    queryFields: function(table_name, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
        };
        this.sendRequest("query_fields", "", args, callback_success, callback_failed, context);
    },

    queryTable: function(table_name, callback_success, callback_failed, context) {
        var args = {
            table: table_name
        };
        this.sendRequest("query_table", "", args, callback_success, callback_failed, context);
    },

    queryRecord: function(table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("query_record", "", args, callback_success, callback_failed, context);
    },

    queryTypeclassTable: function(typeclass, callback_success, callback_failed, context) {
        var args = {
            typeclass: typeclass
        };
        this.sendRequest("query_typeclass_table", "", args, callback_success, callback_failed, context);
    },

    queryForm: function(table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
            record: record_id,
        };
        this.sendRequest("query_form", "", args, callback_success, callback_failed, context);
    },

    queryObjectForm: function(base_typeclass, obj_typeclass, obj_key, callback_success, callback_failed, context) {
        var args = {
            base_typeclass: base_typeclass,
            obj_typeclass: obj_typeclass,
            object: obj_key
        };
        this.sendRequest("query_object_form", "", args, callback_success, callback_failed, context);
    },

    queryAreas: function(callback_success, callback_failed, context) {
        this.sendRequest("query_areas", "", {}, callback_success, callback_failed, context);
    },

    queryObjectEvents: function(object_key, callback_success, callback_failed, context) {
        var args = {
            object: object_key
        };
        this.sendRequest("query_object_events", "", args, callback_success, callback_failed, context);
    },

    queryDialogueSentences: function(dialogue_key, callback_success, callback_failed, context) {
        var args = {
            dialogue: dialogue_key
        };
        this.sendRequest("query_dialogue_sentences", "", args, callback_success, callback_failed, context);
    },

    /*  Query an event action's data.
     *  Args:
     *      type: (string) action's type.
     *      key: （string) action's key.
     */
    queryEventActionData: function(type, key, callback_success, callback_failed, context) {
        var args = {
            type: type,
            key: key
        };
        this.sendRequest("query_event_action_data", "", args, callback_success, callback_failed, context);
    },

    saveForm: function(values, table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            values: values,
            table: table_name,
            record: record_id
        };
        this.sendRequest("save_form", "", args, callback_success, callback_failed, context);
    },

    saveObjectForm: function(tables, base_typeclass, obj_key, callback_success, callback_failed, context) {
        var args = {
            tables: tables,
            base_typeclass: base_typeclass,
            object: obj_key
        };
        this.sendRequest("save_object_form", "", args, callback_success, callback_failed, context);
    },

    deleteRecord: function(table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("delete_record", "", args, callback_success, callback_failed, context);
    },

    queryTables: function(callback_success, callback_failed, context) {
        this.sendRequest("query_tables", "", {}, callback_success, callback_failed, context);
    },

    uploadDataZip: function(file_obj, callback_success, callback_failed, context) {
        this.sendFile("upload_zip", "", file_obj, {}, callback_success, callback_failed, context);
    },

    uploadResourceZip: function(file_obj, callback_success, callback_failed, context) {
        this.sendFile("upload_resources", "", file_obj, {}, callback_success, callback_failed, context);
    },

    uploadSingleData: function(file_obj, table_name, callback_success, callback_failed, context) {
        var args = {
            table: table_name
        };
        this.sendFile("upload_single_data", "", file_obj, args, callback_success, callback_failed, context);
    },

    uploadImage: function(file_obj, field_name, file_type, callback_success, callback_failed, context) {
        var args = {
            field: field_name,
            type: file_type
        };
        this.sendFile("upload_image", "", file_obj, args, callback_success, callback_failed, context);
    },

    queryDataFileTypes: function(callback_success, callback_failed, context) {
        this.sendRequest("query_data_file_types", "", {}, callback_success, callback_failed, context);
    },

    downloadDataZip: function(file_type) {
        var args = {
            type: file_type
        };
        this.downloadFile("download_zip", "", args);
    },

    downloadResourceZip: function() {
        this.downloadFile("download_resources", "", {});
    },

    downloadSingleData: function(table_name, file_type) {
        var args = {
            table: table_name,
            type: file_type
        };
        this.downloadFile("download_single_data", "", args);
    },

    applyChanges: function(callback_success, callback_failed, context) {
        this.sendRequest("apply_changes", "", {}, callback_success, callback_failed, context);
    },

    checkStatus: function(callback_success, callback_failed, context) {
        this.sendRequest("status", "", {}, callback_success, callback_failed, context);
    },
}


