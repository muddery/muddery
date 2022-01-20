
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

    set_token: function(token) {
        sessionStorage.setItem("token", token);
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

    queryElementTable: function(element_type, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_table", "", args, callback_success, callback_failed, context);
    },

    queryForm: function(table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("query_form", "", args, callback_success, callback_failed, context);
    },

    queryFormFirstRecord: function(table_name, callback_success, callback_failed, context) {
        var args = {
            table: table_name
        };
        this.sendRequest("query_form_first_record", "", args, callback_success, callback_failed, context);
    },

    queryElementForm: function(base_element_type, obj_element_type, element_key, callback_success, callback_failed, context) {
        var args = {
            base_element_type: base_element_type,
            obj_element_type: obj_element_type,
            element_key: element_key
        };
        this.sendRequest("query_element_form", "", args, callback_success, callback_failed, context);
    },

    queryAreas: function(callback_success, callback_failed, context) {
        this.sendRequest("query_areas", "", {}, callback_success, callback_failed, context);
    },

    /*  Query all events of the element.
     *  Args:
     *      element_key: (string) the element's key.
     */
    queryElementEventTriggers: function(element_type, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_event_triggers", "", args, callback_success, callback_failed, context);
    },

    /*  Query all events of dialogues.
     */
    queryDialogueEventTriggers: function(callback_success, callback_failed, context) {
        this.sendRequest("query_dialogue_event_triggers", "", {}, callback_success, callback_failed, context);
    },

    /*  Query all events of the element.
     *  Args:
     *      element_key: (string) the element's key.
     */
    queryElementEvents: function(element_key, callback_success, callback_failed, context) {
        var args = {
            element_key: element_key
        };
        this.sendRequest("query_element_events", "", args, callback_success, callback_failed, context);
    },

    /*  Query all forms of the event action.
     *  Args:
     *      action: (string) action's type.
     *      event: （string) event's key.
     */
    queryEventActionForms: function(action, event, callback_success, callback_failed, context) {
        var args = {
            action: action,
            event: event
        };
        this.sendRequest("query_event_action_forms", "", args, callback_success, callback_failed, context);
    },

    /*  Query a map.
     *  Args:
     *      area_key: (string) map area'e key.
     */
    queryMap: function(area_key, callback_success, callback_failed, context) {
        var args = {
            area: area_key
        };
        this.sendRequest("query_map", "", args, callback_success, callback_failed, context);
    },

    /*  Save room's positions in the map.
     *  Args:
     *      area: (dict) map area's data.
     *      rooms: (list) rooms in this area.
     */
    saveMapPositions: function(area, rooms, callback_success, callback_failed, context) {
        var args = {
            area: area,
            rooms: rooms,
        };
        this.sendRequest("save_map_positions", "", args, callback_success, callback_failed, context);
    },

    /*  Add a new area.
     *  Args:
     *      element_type: (string) the area's element type.
     */
    addArea: function(element_type, width, height, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            width: width,
            height: height
        };
        this.sendRequest("add_area", "", args, callback_success, callback_failed, context);
    },

    /*  Add a new room.
     *  Args:
     *      element_type: (string) the room's element type.
     *      area: (string) an area's key.
     *      position: (list) a list of position data.
     */
    addRoom: function(element_type, area, position, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            area: area,
            position: position
        };
        this.sendRequest("add_room", "", args, callback_success, callback_failed, context);
    },

    /*  Add a new exit.
     *  Args:
     *      element_type: (string) the exit's element type.
     *      location: (string) exit's location
     *      destination: (string) exit's destination
     */
    addExit: function(element_type, location, destination, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            location: location,
            destination: destination
        };
        this.sendRequest("add_exit", "", args, callback_success, callback_failed, context);
    },

    saveForm: function(values, table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            values: values,
            table: table_name,
            record: record_id
        };
        this.sendRequest("save_form", "", args, callback_success, callback_failed, context);
    },

    saveElementForm: function(tables, base_element_type, obj_element_type, obj_key, callback_success, callback_failed, context) {
        var args = {
            tables: tables,
            base_element_type: base_element_type,
            obj_element_type: obj_element_type,
            obj_key: obj_key
        };
        this.sendRequest("save_element_form", "", args, callback_success, callback_failed, context);
    },

    saveEventActionForms: function(values, action_type, event_key, callback_success, callback_failed, context) {
        var args = {
            values: values,
            action: action_type,
            event: event_key
        };
        this.sendRequest("save_event_action_forms", "", args, callback_success, callback_failed, context);
    },

    deleteRecord: function(table_name, record_id, callback_success, callback_failed, context) {
        var args = {
            table: table_name,
            record: record_id
        };
        this.sendRequest("delete_record", "", args, callback_success, callback_failed, context);
    },

    deleteElement: function(element_key, base_element_type, callback_success, callback_failed, context) {
        var args = {
            element_key: element_key,
            base_element_type: base_element_type
        };
        this.sendRequest("delete_element", "", args, callback_success, callback_failed, context);
    },

    deleteElements: function(elements, callback_success, callback_failed, context) {
        var args = {
            elements: elements
        };
        this.sendRequest("delete_elements", "", args, callback_success, callback_failed, context);
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

    queryAllElements: function(callback_success, callback_failed, context) {
        this.sendRequest("query_all_elements", "", {}, callback_success, callback_failed, context);
    },

    queryElementTypeProperties: function(element_type, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type
        };
        this.sendRequest("query_element_type_properties", "", args, callback_success, callback_failed, context);
    },

    queryElementProperties: function(element_type, element_key, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            element_key: element_key
        };
        this.sendRequest("query_element_properties", "", args, callback_success, callback_failed, context);
    },

    queryElementLevelProperties: function(element_type, element_key, level, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level
        };
        this.sendRequest("query_element_level_properties", "", args, callback_success, callback_failed, context);
    },

    queryDialoguesTable: function(callback_success, callback_failed, context) {
        this.sendRequest("query_dialogues_table", "", {}, callback_success, callback_failed, context);
    },

    saveElementLevelProperties: function(element_type, element_key, level, values, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level,
            values: values
        };
        this.sendRequest("save_element_level_properties", "", args, callback_success, callback_failed, context);
    },

    deleteElementLevelProperties: function(element_type, element_key, level, callback_success, callback_failed, context) {
        var args = {
            element_type: element_type,
            element_key: element_key,
            level: level
        };
        this.sendRequest("delete_element_level_properties", "", args, callback_success, callback_failed, context);
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
    }
}


