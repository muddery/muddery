
/*
 * Derive from the base class.
 */
MapEditor = function() {
    this.room_typeclass = "ROOM";

    this.room_index = 0;
    this.path_index = 0;

    this.current_room = null;
    this.room_offset_x = 0;
    this.room_offset_y = 0;
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
MapEditor.prototype.createRoom = function(room_key, room_name, x, y) {
    this.rooms[room_key] = {
        name: room_name,
        x: x,
        y: y,
        paths: {}
    }

    var room = $("<div>")
        .attr("id", "room-" + room_key)
        .data("key", room_key)
        .addClass("element-room")
        .appendTo($("#container"));

    room.css({
        "left": x - room.outerWidth() / 2,
        "top": y - room.outerHeight() / 2,
        "position": "absolute"
    });

    var name = $("<div>")
        .attr("id", "roomname-" + room_key)
        .addClass("element-room-name")
        .text(room_name)
        .appendTo($("#container"));

    var width = name.width();

    name.css({
        "left": x - name.width() / 2,
        "top": room.position().top + room.outerHeight(),
        "position": "absolute"});

}



/*
 * Create a path.
 */
MapEditor.prototype.createPath = function(exit_key, source_id, target_id) {
    var path_id = "";
    if (source_id <= target_id) {
        path_id = source_id + "-" + target_id;
    }
    else {
        path_id = target_id + "-" + source_id;
    }

    if (path_id in this.paths) {
        // Add an exit.
        this.paths[path_id].exits.push({
            exit_key: exit_key,
            source: source_id,
            target: target_id
        });
        return;
    }

    // Add a new path.
    // Draw a line from the source room  to the target room.
    var source_room = $("#room-" + source_id);
    var x1 = source_room.position().left + source_room.outerWidth() / 2;
    var y1 = source_room.position().top + source_room.outerHeight() / 2;

    var target_room = $("#room-" + target_id);
    var x2 = target_room.position().left + target_room.outerWidth() / 2;
    var y2 = target_room.position().top + target_room.outerHeight() / 2;

    var svg = document.getElementById("map-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var path = document.createElementNS(namespace, "path");
    path.setAttribute("id", path_id);
    path.setAttribute("stroke", "#777");
    path.setAttribute("stroke-width", "5");
    path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
    path.addEventListener("click", this.onPathClick);
    svg.appendChild(path);

    // Add records.
    this.paths[path_id] = {
        room1: source_id,
        room2: target_id,
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2,
        exits: [
            {
                exit_key: exit_key,
                source: source_id,
                target: target_id
            }
        ]
    }

    this.rooms[source_id].paths[path_id] = "";
    this.rooms[target_id].paths[path_id] = "";
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
    var container = $("#container");
    this.mode = "NEW_ROOM";

    var target = $(event.currentTarget);

    this.room_offset_x = event.clientX - target.offset().left;
    this.room_offset_y = event.clientY - target.offset().top;
    this.current_room = target.clone();
    this.current_room.appendTo(container);

    this.newRoomMouseMove(event);
}


/*
 * Mouse down on a selected room.
 */
MapEditor.prototype.selectedRoomMouseDown = function(event) {
    // Drag the room.
    this.mode = "SELECTED_ROOM";
    this.current_room = $(event.currentTarget);
    this.room_offset_x = event.clientX - this.current_room.offset().left;
    this.room_offset_y = event.clientY - this.current_room.offset().top;
}


/*
 * Mouse down on an unselected room.
 */
MapEditor.prototype.unselectedRoomMouseDown = function(event) {
    // Drag the room.
    this.mode = "UNSELECTED_ROOM";
    this.current_room = $(event.currentTarget);
    this.room_offset_x = event.clientX - this.current_room.offset().left;
    this.room_offset_y = event.clientY - this.current_room.offset().top;
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
        "left": x - this.room_offset_x,
        "top": y - this.room_offset_y,
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
    path.setAttribute("stroke-width", "5");
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

    var width = controller.current_room.outerWidth();
    var height = controller.current_room.outerHeight();

    var room_x = x - this.room_offset_x + width / 2;
    var room_y = y - this.room_offset_y + height / 2;

    // Move the room.
    controller.current_room.css({
        "left": room_x - width / 2,
        "top": room_y - height / 2,
        "position": "absolute"});

    // Move the room's name.
    var room_key = controller.current_room.data("key");
    var name = $("#roomname-" + room_key);
    name.css({
        "left": room_x - name.width() / 2,
        "top": room_y + height / 2,
        "position": "absolute"});

    controller.rooms[room_key].x = room_x;
    controller.rooms[room_key].y = room_y;

    // Move linked paths.
    for (var path_id in controller.rooms[room_key].paths) {
        var path_info = controller.paths[path_id];
        var x1 = path_info.x1;
        var y1 = path_info.y1;
        var x2 = path_info.x2;
        var y2 = path_info.y2;

        if (room_key == path_info.room1) {
            x1 = room_x;
            y1 = room_y;

            controller.paths[path_id]["x1"] = room_x;
            controller.paths[path_id]["y1"] = room_y;
        }
        else if (room_key == path_info.room2) {
            x2 = room_x;
            y2 = room_y;

            controller.paths[path_id]["x2"] = room_x;
            controller.paths[path_id]["y2"] = room_y;
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
    var source_id = this.current_room.attr("id");
    var target_id = $(event.currentTarget).attr("id");

    // Remove the dragging path.
    path.parentNode.removeChild(path);

    if (source_id == target_id) {
        // Can not draw a path to itself.
        return;
    }

    // Create a new path.
    controller.path_index++;
    var path_id = "path-" + controller.path_index;
    controller.createPath(path_id, source_id, target_id);

    this.mode = "";
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
    var room_key = "roomnew-" + controller.room_index;

    var container = $("#container");
    var x = this.current_room.position().left + this.current_room.outerWidth() / 2;
    var y = this.current_room.position().top + this.current_room.outerHeight() / 2;

    controller.createRoom(room_key, "", x, y);

    this.current_room.remove()
    this.current_room = null;
    this.mode = "";
}


/*
 * Unselect the room.
 */
MapEditor.prototype.selectedRoomMouseUp = function(event) {
    controller.current_room.removeClass("element-selected");

    // Remove other pop up menus.
    $(".element-menu").remove();

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

    // Remove other pop up menus.
    $(".element-menu").remove();

    // Show this room's menu.
    var room_key = this.current_room.data("key");
    this.showRoomMenu(room_key);

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

    // Remove pop up menus.
    $(".element-menu").remove();
}


/*
 * Click a path.
 */
MapEditor.prototype.onPathClick = function(event) {
    var path_id = event.target.getAttribute("id");
    controller.showPathMenu(path_id);
}


/***********************************
 *
 * Menus.
 *
 ***********************************/

/*
 * Display a room's menu.
 */
MapEditor.prototype.showRoomMenu = function(room_key) {
    var room_info = controller.rooms[room_key];

    var x = room_info.x - 20;
    var y = room_info.y + 40;

    var menu = $("<div>")
        .addClass("element-menu")
        .css({
            "left": x,
            "top": y,
            "position": "absolute"
        });

    $("<div>")
        .addClass("menu-item edit-room")
        .data("key", room_key)
        .text("Edit")
        .on("mouseup", this.onEditRoom)
        .appendTo(menu);

    $("<div>")
        .addClass("menu-item delete-room")
        .text("Delete")
        .appendTo(menu);

    menu.appendTo($("#container"));
}


/*
 * Display a path's menu.
 */
MapEditor.prototype.showPathMenu = function(path_id) {
    var path_info = controller.paths[path_id];

    var x = (path_info.x1 + path_info.x2) / 2;
    var y = (path_info.y1 + path_info.y2) / 2;

    var menu = $("<div>")
        .addClass("element-menu")
        .css({
            "left": x,
            "top": y,
            "position": "absolute"
        });

    for (var i = 0; i < path_info.exits.length; i++) {
        $("<div>")
            .addClass("menu-item")
            .text(path_info.exits[i].exit_key)
            .appendTo(menu);
    }

    menu.appendTo($("#container"));
}


/*
 * On click the button of edit room.
 */
MapEditor.prototype.onEditRoom = function(event) {
    var room_key = $(this).data("key");
    window.parent.controller.editObject(controller.room_typeclass, room_key);

    // Prevent the container's event.
    event.stopPropagation();
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

    if ("exit" in data) {
        for (var i = 0; i < data.exit.length; i++) {
            var exit_info = data.exit[i];

            if (!(exit_info.location in controller.rooms)) {
            }
            else if (!(exit_info.destination in controller.rooms)) {
            }
            else {
                controller.createPath(exit_info.key, exit_info.location, exit_info.destination);
            }
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