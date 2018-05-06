
/*
 * callback_success: function(data)
 * callback_error: function(code, message, data)
 */
service = {
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
		    success: function(data) {
                if (!data) {
		            data = {
                        code: -1,
                        result: "Empty result.",
                    };
	            }
	            else if (!("code" in data) || !("result" in data)) {
                    data = {
                        code: -1,
                        result: "Wrong result format.",
                    };
	            }
	            
                if (data.code != 0) {
		            console.warn("Return error: " + data.code + "：" + data.result.msg);
		            if (callback_error) {
			            callback_error(data.code, data.result.msg, data.result.data);
		            }
	            }
	            else {
		            if (callback_success) {
			            callback_success(data.result);
		            }
	            }
            },
		    error: function(request, status) {
                if (callback_error) {
                    callback_error(-2, request.statusText, request.status);
                }
            },
	    });
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
}


