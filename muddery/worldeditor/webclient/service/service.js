
/*
 * callback_success: function(data)
 * callback_failed: function(code, message, data)
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

    sendRequest: function(path, func_no, args, callback_success, callback_failed) {
	    var url = CONFIG.api_url + path;
	    var params = {
            func: func_no,
            args: args,
        };

        var headers = {};
        var token = sessionStorage.getItem("token");
        if (token) {
            headers["Authorization"] = "Bearer " + token;
        }

	    $.ajax({
            url: url,
		    type: "POST",
            contentType: "application/json",
            headers: headers,
		    cache: false,
		    data: JSON.stringify(params),
		    dataType: "json",
		    success: this.onSuccess(callback_success, callback_failed),
		    error: this.onError(callback_failed)
	    });
    },

    sendFile: function(path, func_no, file_obj, args, callback_success, callback_failed) {
	    var url = CONFIG.api_url + path;

        var form_file = new FormData();
        form_file.append("func", func_no);
        form_file.append("args", JSON.stringify(args));
        form_file.append("file", file_obj);

        var headers = {};
        var token = sessionStorage.getItem("token");
        if (token) {
            headers["Authorization"] = "Bearer " + token;
        }

        $.ajax({
            url: url,
            type: "POST",
            contentType: false,
            headers: headers,
            cache: false,
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

        var token = sessionStorage.getItem("token");
        if (token) {
            $("<input>")
                .attr("name", "token")
                .attr("value", token)
                .appendTo(form);
        }

        form.appendTo('body').submit().remove();
    },

    set_token: function(token) {
        sessionStorage.setItem("token", token);
    },

    login: function(username, password, callback_success, callback_failed) {
        var args = {
            username: username,
            password: password
        };
        this.sendRequest("login", "", args, callback_success, callback_failed);
    },

    logout: function(callback_success, callback_failed) {
        this.sendRequest("logout", "", {}, callback_success, callback_failed);
    },

    queryTable: function(table_name, callback_success, callback_failed) {
        var args = {
            table: table_name
        };
        this.sendRequest("query_table", "", args, callback_success, callback_failed);
    },

    queryRecord: function(table_name, record_id, callback_success, callback_failed) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("query_record", "", args, callback_success, callback_failed);
    },

    queryElementTable: function(element_type, callback_success, callback_failed) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_table", "", args, callback_success, callback_failed);
    },

    queryForm: function(table_name, record_id, callback_success, callback_failed) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("query_form", "", args, callback_success, callback_failed);
    },

    queryFormFirstRecord: function(table_name, callback_success, callback_failed) {
        var args = {
            table: table_name
        };
        this.sendRequest("query_form_first_record", "", args, callback_success, callback_failed);
    },

    queryElementForm: function(base_element_type, obj_element_type, element_key, callback_success, callback_failed) {
        var args = {
            base_element_type: base_element_type,
            obj_element_type: obj_element_type,
            element_key: element_key
        };
        this.sendRequest("query_element_form", "", args, callback_success, callback_failed);
    },

    queryAreas: function(callback_success, callback_failed) {
        this.sendRequest("query_areas", "", {}, callback_success, callback_failed);
    },

    /*  Query all events of the element.
     *  Args:
     *      element_key: (string) the element's key.
     */
    queryElementEventTriggers: function(element_type, callback_success, callback_failed) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_event_triggers", "", args, callback_success, callback_failed);
    },

    /*  Query all events of dialogues.
     */
    queryDialogueEventTriggers: function(callback_success, callback_failed) {
        this.sendRequest("query_dialogue_event_triggers", "", {}, callback_success, callback_failed);
    },

    /*  Query all events of the element.
     *  Args:
     *      element_key: (string) the element's key.
     */
    queryElementEvents: function(element_key, callback_success, callback_failed) {
        var args = {
            element_key: element_key
        };
        this.sendRequest("query_element_events", "", args, callback_success, callback_failed);
    },

    /*  Query all forms of the event action.
     *  Args:
     *      action: (string) action's type.
     *      event: （string) event's key.
     */
    queryEventActionForms: function(action, event, callback_success, callback_failed) {
        var args = {
            action: action,
            event: event
        };
        this.sendRequest("query_event_action_forms", "", args, callback_success, callback_failed);
    },

    /*  Query a map.
     *  Args:
     *      area_key: (string) map area'e key.
     */
    queryMap: function(area_key, callback_success, callback_failed) {
        var args = {
            area: area_key
        };
        this.sendRequest("query_map", "", args, callback_success, callback_failed);
    },

    /*  Save room's positions in the map.
     *  Args:
     *      area: (dict) map area's data.
     *      rooms: (list) rooms in this area.
     */
    saveMapPositions: function(area, rooms, callback_success, callback_failed) {
        var args = {
            area: area,
            rooms: rooms,
        };
        this.sendRequest("save_map_positions", "", args, callback_success, callback_failed);
    },

    /*  Add a new area.
     *  Args:
     *      element_type: (string) the area's element type.
     */
    addArea: function(element_type, width, height, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            width: width,
            height: height
        };
        this.sendRequest("add_area", "", args, callback_success, callback_failed);
    },

    /*  Add a new room.
     *  Args:
     *      element_type: (string) the room's element type.
     *      area: (string) an area's key.
     *      position: (list) a list of position data.
     */
    addRoom: function(element_type, area, position, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            area: area,
            position: position
        };
        this.sendRequest("add_room", "", args, callback_success, callback_failed);
    },

    /*  Add a new exit.
     *  Args:
     *      element_type: (string) the exit's element type.
     *      location: (string) exit's location
     *      destination: (string) exit's destination
     */
    addExit: function(element_type, location, destination, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            location: location,
            destination: destination
        };
        this.sendRequest("add_exit", "", args, callback_success, callback_failed);
    },

    saveForm: function(values, table_name, record_id, callback_success, callback_failed) {
        var args = {
            values: values,
            table: table_name,
            record: record_id
        };
        this.sendRequest("save_form", "", args, callback_success, callback_failed);
    },

    saveElementForm: function(tables, base_element_type, obj_element_type, obj_key, callback_success, callback_failed) {
        var args = {
            tables: tables,
            base_element_type: base_element_type,
            obj_element_type: obj_element_type,
            obj_key: obj_key
        };
        this.sendRequest("save_element_form", "", args, callback_success, callback_failed);
    },

    saveEventActionForms: function(values, action_type, event_key, callback_success, callback_failed) {
        var args = {
            values: values,
            action: action_type,
            event: event_key
        };
        this.sendRequest("save_event_action_forms", "", args, callback_success, callback_failed);
    },

    deleteRecord: function(table_name, record_id, callback_success, callback_failed) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("delete_record", "", args, callback_success, callback_failed);
    },

    deleteElement: function(element_key, base_element_type, callback_success, callback_failed) {
        var args = {
            element_key: element_key,
            base_element_type: base_element_type
        };
        this.sendRequest("delete_element", "", args, callback_success, callback_failed);
    },

    deleteElements: function(elements, callback_success, callback_failed) {
        var args = {
            elements: elements
        };
        this.sendRequest("delete_elements", "", args, callback_success, callback_failed);
    },

    queryTables: function(callback_success, callback_failed) {
        this.sendRequest("query_tables", "", {}, callback_success, callback_failed);
    },

    uploadDataZip: function(file_obj, callback_success, callback_failed) {
        this.sendFile("upload_zip", "", file_obj, {}, callback_success, callback_failed);
    },

    uploadResourceZip: function(file_obj, callback_success, callback_failed) {
        this.sendFile("upload_resources", "", file_obj, {}, callback_success, callback_failed);
    },

    uploadSingleData: function(file_obj, table_name, callback_success, callback_failed) {
        var args = {
            table: table_name
        };
        this.sendFile("upload_single_data", "", file_obj, args, callback_success, callback_failed);
    },

    uploadImage: function(file_obj, field_name, file_type, callback_success, callback_failed) {
        var args = {
            field: field_name,
            type: file_type
        };
        this.sendFile("upload_image", "", file_obj, args, callback_success, callback_failed);
    },

    queryDataFileTypes: function(callback_success, callback_failed) {
        this.sendRequest("query_data_file_types", "", {}, callback_success, callback_failed);
    },

    queryAllElements: function(callback_success, callback_failed) {
        this.sendRequest("query_all_elements", "", {}, callback_success, callback_failed);
    },

    queryElementTypeProperties: function(element_type, callback_success, callback_failed) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_type_properties", "", args, callback_success, callback_failed);
    },

    queryElementProperties: function(element_type, element_key, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            element_key: element_key
        };
        this.sendRequest("query_element_properties", "", args, callback_success, callback_failed);
    },

    queryElementLevelProperties: function(element_type, element_key, level, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level
        };
        this.sendRequest("query_element_level_properties", "", args, callback_success, callback_failed);
    },

    queryConditionalDesc: function(element_type, element_key, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            element_key: element_key,
        };
        this.sendRequest("query_conditional_desc", "", args, callback_success, callback_failed);
    },

    queryDialoguesTable: function(callback_success, callback_failed) {
        this.sendRequest("query_dialogues_table", "", {}, callback_success, callback_failed);
    },

    saveElementLevelProperties: function(element_type, element_key, level, values, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level,
            values: values
        };
        this.sendRequest("save_element_level_properties", "", args, callback_success, callback_failed);
    },

    deleteElementLevelProperties: function(element_type, element_key, level, callback_success, callback_failed) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level
        };
        this.sendRequest("delete_element_level_properties", "", args, callback_success, callback_failed);
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

    applyChanges: function(callback_success, callback_failed) {
        this.sendRequest("apply_changes", "", {}, callback_success, callback_failed);
    },

    checkStatus: function(callback_success, callback_failed) {
        this.sendRequest("status", "", {}, callback_success, callback_failed);
    }
}


