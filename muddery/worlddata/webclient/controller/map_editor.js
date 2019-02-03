
/*
 * Derive from the base class.
 */
MapEditor = function() {
    this.room_index = 0;
    this.path_index = 0;

    this.current_room = null;
    this.current_path = null;
    this.mode = "";

    this.map_data = {};

    // All rooms and paths.
    this.background = "";
    this.rooms = {};
    this.paths = {};
    this.room_paths = {};
}

MapEditor.prototype.init = function() {
    this.area_key = utils.getQueryString("map");

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.obj_key) {
        $("#delete-record").removeClass("hidden");
    }

    $("#form-name").text(this.area_key);

    this.onImageLoad();
    this.bindEvents();
    this.refresh();
}

MapEditor.prototype.bindEvents = function() {
    $("#exit-button").on("click", this.onExit);
    $("#save-record").on("click", this.onSave);
    $("#delete-record").on("click", this.onDelete);

    $("#map-image").on("load", this.onImageLoad);

    // Mouse down on a room.
    $("#container").on("mousedown", ".element-room", this.onRoomMouseDown);

    // Mouse move on the container.
    $("#container").on("mousemove", this.onMouseMove);

    // Mouse up on a room.
    $("#container").on("mouseup", ".element-room", this.onRoomMouseUp);

    // Mouse up on the container.
    $("#container").on("mouseup", this.onContainerMouseUp);
}

MapEditor.prototype.onExit = function() {
    controller.exitNoChange();
}

MapEditor.prototype.onSave = function() {
    controller.saveMap(controller.saveMapSuccess, controller.saveMapFailed);
}

MapEditor.prototype.onDelete = function() {
    window.parent.controller.confirm("",
                                     "Delete this map?",
                                     controller.confirmDelete);
}


/*
 * On the map's background loaded.
 */
MapEditor.prototype.onImageLoad = function() {
    if (!controller.background) {
        return;
    }

    // Get the image's original size.
    var image = document.getElementById("map-image");
    var width = image.naturalWidth;
    var height = image.naturalHeight;

    $("#container").width(width);
    $("#container").height(height);

    $("#map-svg").width(width);
    $("#map-svg").height(height);

    $("#map-image").width(width);
    $("#map-image").height(height);

    $("#image-width").val(width);
    $("#image-height").val(height);
}

MapEditor.prototype.onSave = function() {
    // Upload images before submit the form.
    var upload_images = false;
    controller.file_fields = [];

    var image_fields = $(".image-input-control");
    for (var i = 0; i < image_fields.length; i++) {
        var file_obj = image_fields[i].files[0];
        if (file_obj && file_obj.size > 0) {
            upload_images = true;
            var image_type = $(image_fields[i]).data("image_type");
            var name = $(image_fields[i]).data("field_name");
            controller.file_fields.push(name);
            service.uploadImage(file_obj, name, image_type, controller.uploadSuccess(name), controller.uploadFailed);
        }
    }

    if (!upload_images) {
        controller.saveFields(controller.saveFormSuccess, controller.saveFormFailed);
    }
}

MapEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    service.deleteObject(controller.base_typeclass,
                         controller.obj_key,
                         controller.deleteSuccess);
}

MapEditor.prototype.onUpload = function(e) {
    var record_id = $(this).attr("data-record-id");
    if (record_id) {
        var editor = "event";
        var table = "event_data";
        var args = {
            trigger: controller.obj_key,
        }
        window.parent.controller.editRecord(editor, table, record_id, args);
    }
}

MapEditor.prototype.onDeleteEvent = function(e) {
    var record_id = $(this).attr("data-record-id");
    window.parent.controller.confirm("",
                                     "Delete this record?",
                                     controller.confirmDeleteEvent,
                                     {record: record_id});
}

MapEditor.prototype.confirmDeleteEvent = function(e) {
    window.parent.controller.hideWaiting();

    var table = controller.table_name;
    var record_id = e.data.record;
    service.deleteRecord(table, record, this.deleteEventSuccess);
}

MapEditor.prototype.deleteEventSuccess = function(data) {
    var record_id = data.record;
    $("#event-table").bootstrapTable("remove", {
        field: "id",
        values: [record_id],
    });
}


/***********************************
 *
 * Draw map.
 *
 ***********************************/

/*
 * Create a new room.
 */
MapEditor.prototype.createRoom = function(room_id, room_name, x, y) {
    this.rooms[room_id] = {
        paths: {}
    }

    var room = $("<div>")
        .attr("id", room_id)
        .addClass("element-room")
        .appendTo($("#container"));

    room.css({
        "left": x - room.outerWidth() / 2,
        "top": y - room.outerHeight() / 2,
        "position": "absolute"
    });

    var name = $("<div>")
        .attr("id", room_id + "-name")
        .addClass("element-room-name")
        .text(room_name)
        .appendTo($("#container"));

    var width = name.width();

    name.css({
        "left": x - name.width() / 2,
        "top": room.position().top + room.outerHeight(),
        "position": "absolute"});

}


/***********************************
 *
 * Mouse down event.
 *
 ***********************************/

/*
 * On mouse down on a room.
 */
MapEditor.prototype.onRoomMouseDown = function(event) {
    if ($(this).hasClass("new-element")) {
        // On a new room.
        controller.newRoomMouseDown(event);
    }
    else if ($(this).hasClass("element-selected")) {
        // On a selected room.
        controller.selectedRoomMouseDown(event);
    }
    else {
        // On an unselected room.
        controller.unselectedRoomMouseDown(event);
    }
}


/*
 * Mouse down on a new room.
 */
MapEditor.prototype.newRoomMouseDown = function(event) {
    // Drag the room.
    this.mode = "NEW_ROOM";
    this.current_room = $(event.currentTarget).clone();
    this.current_room.appendTo($("#container"));

    this.newRoomMouseMove(event);
}


/*
 * Mouse down on a selected room.
 */
MapEditor.prototype.selectedRoomMouseDown = function(event) {
    // Drag the room.
    this.mode = "SELECTED_ROOM";
    this.current_room = $(event.currentTarget);
}


/*
 * Mouse down on an unselected room.
 */
MapEditor.prototype.unselectedRoomMouseDown = function(event) {
    // Drag the room.
    this.mode = "UNSELECTED_ROOM";
    this.current_room = $(event.currentTarget);
}


/***********************************
 *
 * Mouse move event.
 *
 ***********************************/

/*
 * Mouse move on the container.
 */
MapEditor.prototype.onMouseMove = function(event) {
    if (controller.mode == "") {
        return;
    }
    else if (controller.mode == "NEW_ROOM") {
        // Move a new room.
        controller.newRoomMouseMove(event);
    }
    else if (controller.mode == "SELECTED_ROOM") {
        // Move on a selected room.
        controller.selectedRoomMouseMove(event);
    }
    else if (controller.mode == "UNSELECTED_ROOM") {
        // Move on an unselected room.
        controller.unselectedRoomMouseMove(event);
    }
    else if (controller.mode == "DRAG_PATH") {
        // Drag a new path.
        controller.dragPath(event);
    }
    else if (controller.mode == "DRAG_ROOM") {
        // Drag a room.
        controller.dragRoom(event);
    }
}


/*
 * Move a new room.
 */
MapEditor.prototype.newRoomMouseMove = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    // Move the room.
    controller.current_room.css({
        "left": x - controller.current_room.outerWidth() / 2,
        "top": y - controller.current_room.outerHeight() / 2,
        "position": "absolute"});
}


/*
 * Move a selected room.
 */
MapEditor.prototype.selectedRoomMouseMove = function(event) {
    this.mode = "DRAG_PATH";

    // Create a new path.
    var svg = document.getElementById("map-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var path = document.createElementNS(namespace, "path");
    path.setAttribute("id", "map-path");
    path.setAttribute("stroke", "#555");
    svg.appendChild(path);
    this.current_path = path;

    this.dragPath(event);
}


/*
 * Move an unselected room.
 */
MapEditor.prototype.unselectedRoomMouseMove = function(event) {
    this.mode = "DRAG_ROOM";
    this.dragRoom(event);
}


/*
 * Drag a new path.
 */
MapEditor.prototype.dragPath = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    var x1 = controller.current_room.position().left + controller.current_room.outerWidth() / 2;
    var y1 = controller.current_room.position().top + controller.current_room.outerHeight() / 2;
    var x2 = x;
    var y2 = y;

    this.current_path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
}


/*
 * Drag a room.
 */
MapEditor.prototype.dragRoom = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    // Move the room.
    controller.current_room.css({
        "left": x - controller.current_room.outerWidth() / 2,
        "top": y - controller.current_room.outerHeight() / 2,
        "position": "absolute"});

    // Move the room's name.
    var room_id = controller.current_room.attr("id");
    var height = controller.current_room.outerHeight();
    var name = $("#" + room_id + "-name");
    name.css({
        "left": x - name.width() / 2,
        "top": y + height / 2,
        "position": "absolute"});

    // Move linked paths.
    for (var path_id in controller.rooms[room_id].paths) {
        var path_info = controller.paths[path_id];
        var x1 = path_info.source_x;
        var y1 = path_info.source_y;
        var x2 = path_info.target_x;
        var y2 = path_info.target_y;

        if (room_id == path_info.source) {
            x1 = x;
            y1 = y;

            controller.paths[path_id]["source_x"] = x;
            controller.paths[path_id]["source_y"] = y;
        }
        else if (room_id == path_info.target) {
            x2 = x;
            y2 = y;

            controller.paths[path_id]["target_x"] = x;
            controller.paths[path_id]["target_y"] = y;
        }

        // Move path.
        var path = document.getElementById(path_id);
        path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
    }
}


/***********************************
 *
 * Mouse up event.
 *
 ***********************************/

/*
 * On mouse up on a room.
 */
MapEditor.prototype.onRoomMouseUp = function(event) {
    if (controller.mode == "DRAG_PATH") {
        // Drop the new path.
        controller.dropPathOnRoom(event);
    }
}


/*
 * Drop the new path on a room.
 */
MapEditor.prototype.dropPathOnRoom = function(event) {
    var path = this.current_path;
    var target = $(event.currentTarget);
    var source_id = this.current_room.attr("id");
    var target_id = target.attr("id");
    if (source_id == target_id) {
        // Remove the path.
        path.parentNode.removeChild(path);
    }

    // Link to the target room.
    var x1 = controller.current_room.position().left + controller.current_room.outerWidth() / 2;
    var y1 = controller.current_room.position().top + controller.current_room.outerHeight() / 2;

    var position = target.position();
    var width = target.outerWidth();
    var height = target.outerHeight();
    var x2 = position.left + width / 2;
    var y2 = position.top + height / 2;
    path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);

    // Rename the path.
    controller.path_index++;
    var path_id = "path-" + controller.path_index;
    path.setAttribute("id", path_id);

    // Save this path.
    var source_id = controller.current_room_id;
    var target_id = $(this).attr("id");
    controller.addPath(path_id, source_id, x1, y1, target_id, x2, y2);

    event.stopPropagation();
}


/*
 * On mouse up on the container.
 */
MapEditor.prototype.onContainerMouseUp = function(event) {
    if (controller.mode == "NEW_ROOM") {
        // Drop a new room.
        controller.newRoomMouseUp(event);
    }
    else if (controller.mode == "SELECTED_ROOM") {
        // Unselect the room.
        controller.selectedRoomMouseUp(event);
    }
    else if (controller.mode == "UNSELECTED_ROOM") {
        // Select the room.
        controller.unselectedRoomMouseUp(event);
    }
    else if (controller.mode == "DRAG_PATH") {
        // Drop a new path.
        controller.dropPath(event);
    }
    else if (controller.mode == "DRAG_ROOM") {
        // Drop a room.
        controller.dropRoom(event);
    }
    else {
        controller.containerMouseUp(event);
    }
}


/*
 * Drop a new room.
 */
MapEditor.prototype.newRoomMouseUp = function(event) {
    controller.room_index++;
    var room_id = "room-" + controller.room_index;

    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    controller.createRoom(room_id, "", x, y);

    this.current_room.remove()
    this.current_room = null;
    this.mode = "";
}


/*
 * Unselect the room.
 */
MapEditor.prototype.selectedRoomMouseUp = function(event) {
    controller.current_room.removeClass("element-selected");

    this.current_room = null;
    this.mode = "";
}


/*
 * Select the room.
 */
MapEditor.prototype.unselectedRoomMouseUp = function(event) {
    // Unselect other rooms.
    $(".element-room").removeClass("element-selected");

    // Select this room.
    this.current_room.addClass("element-selected");

    this.mode = "";

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Drop a new path.
 */
MapEditor.prototype.dropPath = function(event) {
    var path = this.current_path;
    path.parentNode.removeChild(path);

    this.current_path = null;
    this.mode = "";

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Drop a room.
 */
MapEditor.prototype.dropRoom = function(event) {
    this.current_room = null;
    this.mode = "";

    // Prevent the container's event.
    event.stopPropagation();
}



/*
 * Click the background to unselect all room.
 */
MapEditor.prototype.containerMouseUp = function(event) {
    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");
}


/*
 * Add a path
 */
MapEditor.prototype.addPath = function(path_id, source_id, source_x, source_y, target_id, target_x, target_y) {
    this.paths[path_id] = {
        source: source_id,
        source_x: source_x,
        source_y: source_y,
        target: target_id,
        target_x: target_x,
        target_y: target_y
    }

    this.rooms[source_id].paths[path_id] = "";
    this.rooms[target_id].paths[path_id] = "";
}


MapEditor.prototype.refresh = function() {
    service.queryMap(this.area_key,
                     this.queryMapSuccess,
                     this.queryMapFailed);
}

MapEditor.prototype.uploadSuccess = function(field_name) {
    var callback = function(data) {
        // Show images when upload images success.
        for (var i = 0; i < controller.file_fields.length; i++) {
            if (controller.file_fields[i] == field_name) {
                controller.file_fields.splice(i, 1);
                var field = $("#control-" + field_name);
                field.find(".editor-control").val(data.resource);
                field.find("img")
                    .attr("src", CONFIG.resource_url + data.resource)
                    .on("load", controller.onImageLoad);
                break;
            }
        }

        // Submit the form.
        if (controller.file_fields.length == 0) {
            controller.saveFields(controller.saveFormSuccess, controller.saveFormFailed);
        }
    }

    return callback;
}

MapEditor.prototype.uploadFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

MapEditor.prototype.queryMapSuccess = function(data) {
    controller.map_data = data;

    // Draw the background.
    var map_scale = 1;
    var map_room_size = 40;
    var original_point_x = 0;
    var original_point_y = 0;

    if ("area" in data) {
        controller.background = data.area.background;
        if (controller.background) {
            $("#map-image")
                .attr("src", CONFIG.resource_url + controller.background);
        }

        map_scale = data.area.map_scale | 1;
        map_room_size = data.area.map_room_size | 40;

        var background_point_x = 0;
        var background_point_y = 0;
        var corresp_pos_x = 0;
        var corresp_pos_y = 0;

        if (data.area.background_point) {
            background_point_x = data.area.background_point[0];
            background_point_y = data.area.background_point[1];
        }

        if (data.area.corresp_map_pos) {
            corresp_pos_x = data.area.corresp_map_pos[0];
            corresp_pos_y = data.area.corresp_map_pos[1];
        }

        original_point_x = background_point_x - corresp_pos_x * map_scale;
        original_point_y = background_point_y + corresp_pos_y * map_scale;
    }

    if ("room" in data) {
        for (var i = 0; i < data.room.length; i++) {
            var room_info = data.room[i];
            var x = 0;
            var y = 0;
            if (room_info.position) {
                x = original_point_x + room_info.position[0] * map_scale;
                y = original_point_y - room_info.position[1] * map_scale;
            }
            controller.createRoom(room_info.key, room_info.name, x, y);
        }
    }
}

MapEditor.prototype.queryMapFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

MapEditor.prototype.exit = function() {
    setInterval(function() {window.parent.controller.popPage(true);}, 0);
}

MapEditor.prototype.exitNoChange = function() {
    setInterval(function() {window.parent.controller.popPage(false);}, 0);
}