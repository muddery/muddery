
/*
 * Derive from the base class.
 */
MapEditor = function() {
    this.area_typeclass = "AREA";
    this.room_typeclass = "ROOM";
    this.exit_typeclass = "EXIT";

    this.blank_map = "../images/blank_map.png";
    this.default_map_width = 400;
    this.default_map_height = 400;
    this.room_size = 40;

    this.path_index = 0;

    this.current_room = null;
    this.room_offset_x = 0;
    this.room_offset_y = 0;
    this.current_path = null;
    this.mode = "";

    this.origin_map = null;

    // All rooms and paths.
    this.background = "";
    this.area_width = 0;
    this.area_height = 0;
    this.rooms = {};
    this.paths = {};
}

MapEditor.prototype.init = function() {
    this.area_key = utils.getQueryString("map");

    $("#discard-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    $("#delete-record").removeClass("hidden");

    $("#form-name").text(this.area_key);

    this.onImageLoad();
    this.bindEvents();
    this.refresh();
}

MapEditor.prototype.bindEvents = function() {
    $("#discard-button").on("click", this.onDiscard);
    $("#save-record").on("click", this.onSave);
    $("#delete-record").on("click", this.onDelete);

    $("#upload-background").on("click", this.onUploadBackground);
    $("#delete-background").on("click", this.onDeleteBackground);
    $("#set-background-size").on("click", this.onSetBackgroundSize);
    $("#restore-background-size").on("click", this.onRestoreBackgroundSize);
    $("#edit-area").on("click", this.onEditArea);

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

MapEditor.prototype.onDiscard = function() {
    window.parent.controller.confirm("",
                                     "Discard changes? (Deleted objects and saved attributes can not be restored.)",
                                     controller.confirmDiscard);
}

MapEditor.prototype.onSave = function() {
    controller.saveMapPositions(controller.saveForExit);
}


MapEditor.prototype.saveForExit = function(data) {
    controller.exit();
}


MapEditor.prototype.onDelete = function() {
    window.parent.controller.confirm("",
                                     "Delete this map and all rooms and exits in it?",
                                     controller.confirmDelete);
}


/*
 * Delete the whole area.
 */
MapEditor.prototype.confirmDelete = function(e) {
    window.parent.controller.hideWaiting();

    var objects = [controller.area_key];

    // Get all rooms.
    objects = objects.concat(Object.keys(controller.rooms));

    // Get all exits.
    for (var key in controller.paths) {
        objects = objects.concat(Object.keys(controller.paths[key].exits));
    }

    service.deleteObjects(objects, controller.deleteAreaSuccess, controller.failedCallback);
}


/*
 * Delete the whole area success.
 */
MapEditor.prototype.deleteAreaSuccess = function(data) {
    controller.exit();
}


/*
 * On the map's background loaded.
 */
MapEditor.prototype.onEditArea = function() {
    controller.saveMapPositions(controller.saveForEditArea);
}

MapEditor.prototype.saveForEditArea = function(data) {
    window.parent.controller.editObject(controller.area_typeclass, controller.area_key);
}


/*
 * Common failed callback.
 */
MapEditor.prototype.failedCallback = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}

/***********************************
 *
 * Background.
 *
 ***********************************/

/*
 * On the map's background loaded.
 */
MapEditor.prototype.onImageLoad = function() {
    if (controller.background && (controller.area_width == 0 || controller.area_height == 0)) {
        // Get the image's original size.
        var image = document.getElementById("map-image");
        controller.area_width = image.naturalWidth;
        controller.area_height = image.naturalHeight;
    }

    controller.setBackgroundSize(controller.area_width, controller.area_height);
}

/*
 * Set the background's size.
 */
MapEditor.prototype.setBackgroundSize = function(width, height) {
    this.area_width = width;
    this.area_height = height;

    $("#container").width(width);
    $("#container").height(height);

    $("#map-svg").width(width);
    $("#map-svg").height(height);

    $("#map-image").width(width);
    $("#map-image").height(height);

    $("#image-width").val(width);
    $("#image-height").val(height);
}

/*
 * On upload the map's background.
 */
MapEditor.prototype.onUploadBackground = function() {
    // Upload images before submit the form.
    var upload_images = false;
    controller.file_fields = [];

    var image_field = document.getElementById("image-input");
    var file_obj = image_field.files[0];
    if (file_obj && file_obj.size > 0) {
        controller.area_width = 0;
        controller.area_height = 0;
        service.uploadImage(file_obj, name, "background", controller.uploadSuccessCallback, controller.failedCallback);
    }
}


MapEditor.prototype.uploadSuccessCallback = function(data) {
    // Show images when upload images success.
    controller.background = data.resource;
    $("#map-image")
        .attr("src", CONFIG.resource_url + data.resource)
        .on("load", controller.onImageLoad);
}


/*
 * On delete the map's background.
 */
MapEditor.prototype.onDeleteBackground = function() {
    window.parent.controller.confirm("",
                                     "Delete this background?",
                                     controller.confirmDeleteBackground);
}

/*
 * On delete the map's background.
 */
MapEditor.prototype.confirmDeleteBackground = function() {
     window.parent.controller.hideWaiting();

    controller.background = "";
    $("#map-image").attr("src", controller.blank_map);
}

/*
 * On click the set background size button.
 */
MapEditor.prototype.onSetBackgroundSize = function() {
    var width = parseInt($("#image-width").val());
    var height = parseInt($("#image-height").val());
    if (!width || !height || width < 0 || height < 0) {
        return;
    }
    controller.setBackgroundSize(width, height);
}

/*
 * On click the restore background size button.
 */
MapEditor.prototype.onRestoreBackgroundSize = function() {
    // Get the image's original size.
    var image = document.getElementById("map-image");
    var width = image.naturalWidth;
    var height = image.naturalHeight;
    controller.setBackgroundSize(width, height);
}

/***********************************
 *
 * Draw map.
 *
 ***********************************/

/*
 * Create a new room.
 */
MapEditor.prototype.createRoom = function(info, x, y) {
    this.rooms[info.key] = {
        info: info,
        x: x,
        y: y,
        paths: {}
    }

    var room = $("<div>")
        .attr("id", "room-" + info.key)
        .data("key", info.key)
        .addClass("element-room")
        .appendTo($("#container"));

    room.css({
        "left": x - room.outerWidth() / 2,
        "top": y - room.outerHeight() / 2,
        "position": "absolute"
    });

    var name = $("<div>")
        .attr("id", "roomname-" + info.key)
        .addClass("element-room-name")
        .text(info.name)
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
MapEditor.prototype.createPath = function(info) {
    var path_id = "";
    if (info.location <= info.destination) {
        path_id = info.location + "-" + info.destination;
    }
    else {
        path_id = info.destination + "-" + info.location;
    }

    if (path_id in this.paths) {
        // Add an exit.
        this.paths[path_id].exits[info.key] = info;
        return;
    }

    // Add a new path.
    // Draw a line from the source room  to the target room.
    var source_room = controller.rooms[info.location];
    var x1 = source_room.x;
    var y1 = source_room.y;

    var target_room = controller.rooms[info.destination];
    var x2 = target_room.x;
    var y2 = target_room.y;

    var svg = document.getElementById("map-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var path = document.createElementNS(namespace, "path");
    path.setAttribute("id", path_id);
    path.setAttribute("stroke", "#666");
    path.setAttribute("stroke-width", "5");
    path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
    path.addEventListener("click", this.onPathClick);
    svg.appendChild(path);

    // Add records.
    this.paths[path_id] = {
        room1: info.location,
        room2: info.destination,
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2,
        exits: {}
    }
    this.paths[path_id].exits[info.key] = info;

    this.rooms[info.location].paths[path_id] = "";
    this.rooms[info.destination].paths[path_id] = "";
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
    // Select a room.
    this.mode = "SELECTED_ROOM";
    this.current_room = $(event.currentTarget);
    this.room_offset_x = event.clientX - this.current_room.offset().left;
    this.room_offset_y = event.clientY - this.current_room.offset().top;
}


/*
 * Mouse down on an unselected room.
 */
MapEditor.prototype.unselectedRoomMouseDown = function(event) {
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

    if (controller.mode == "NEW_ROOM") {
        // Move a new room.
        controller.newRoomMouseMove(event);
    }
    else if (controller.mode == "SELECTED_ROOM") {
        // Move on a selected room.
        // controller.selectedRoomMouseMove(event);
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
 * Move an unselected room.
 */
MapEditor.prototype.unselectedRoomMouseMove = function(event) {
    // Drag the room or drag a new path.
    var width = controller.current_room.innerWidth();
    var height = controller.current_room.innerHeight();
    var relative_x = controller.room_offset_x - controller.current_room.outerWidth() / 2;
    var relative_y = controller.room_offset_y - controller.current_room.outerHeight() / 2;

    if (Math.abs(relative_x) - width / 2　< 0 &&
        Math.abs(relative_y) - height / 2　< 0) {
        this.mode = "DRAG_ROOM";
    }
    else {
        this.mode = "DRAG_PATH";

        // Create a new path.
        var svg = document.getElementById("map-svg");
        var namespace = "http://www.w3.org/2000/svg";
        var path = document.createElementNS(namespace, "path");
        path.setAttribute("id", "map-path");
        path.setAttribute("stroke", "#e30");
        path.setAttribute("stroke-width", "5");
        svg.appendChild(path);
        this.current_path = path;

        this.dragPath(event);
    }
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
    this.mode = "";
    event.stopPropagation();

    if ($(event.currentTarget).hasClass("new-element")) {
        // Can not draw a path to new element buttons.
        controller.finishDraggingPath();
        return;
    }

    var source_key = this.current_room.data("key");
    var target_key = $(event.currentTarget).data("key");

    if (source_key == target_key) {
        // Can not draw a path to itself.
        controller.finishDraggingPath();
        return;
    }

    var path_id = "";
    if (source_key <= target_key) {
        path_id = source_key + "-" + target_key;
    }
    else {
        path_id = target_key + "-" + source_key;
    }
    var new_path = !(path_id in this.paths);

    // Create a new path.
    var exit_info = {
        typeclass: this.exit_typeclass,
        location: source_key,
        destination: target_key
    };
    service.addExit(this.exit_typeclass,
                        source_key,
                        target_key,
                        this.addExitSuccess,
                        this.addExitFailed,
                        exit_info);

    if (new_path) {
        // Add a reverse exit.
        var exit_info = {
            typeclass: this.exit_typeclass,
            location: target_key,
            destination: source_key
        };
        service.addExit(this.exit_typeclass,
                            target_key,
                            source_key,
                            this.addExitSuccess,
                            this.addExitFailed,
                            exit_info);
    }
}


MapEditor.prototype.addExitSuccess = function(data, context) {
    var exit_info = context;
    exit_info["key"] = data.key;

    controller.createPath(exit_info);
    controller.finishDraggingPath();
}


MapEditor.prototype.addExitFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);

    controller.finishDraggingPath();
}


/*
 * Finish dragging the new path.
 */
MapEditor.prototype.finishDraggingPath = function() {
    // Show room menu.
    $(".room-menu").show();

    if (!this.current_path) {
        return;
    }

    // Remove the dragging path.
    this.current_path.parentNode.removeChild(this.current_path);
    this.current_path = null;
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
    var x = this.current_room.position().left + this.current_room.outerWidth() / 2;
    var y = this.current_room.position().top + this.current_room.outerHeight() / 2;

    service.addRoom(this.room_typeclass, this.area_key, [x, y], this.addRoomSuccess, this.addRoomFailed);
}


MapEditor.prototype.addRoomSuccess = function(data) {
    var room_key = data.key;

    var x = controller.current_room.position().left + controller.current_room.outerWidth() / 2;
    var y = controller.current_room.position().top + controller.current_room.outerHeight() / 2;

    var room_info = {
        key: room_key,
        name: "",
        typeclass: controller.room_typeclass,
        position: [x, y]
    }
    controller.createRoom(room_info, x, y);

    controller.current_room.remove()
    controller.current_room = null;
    controller.mode = "";
}


MapEditor.prototype.addRoomFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);

    this.current_room.remove()
    this.current_room = null;
    this.mode = "";
}


/*
 * Unselect the room.
 */
MapEditor.prototype.selectedRoomMouseUp = function(event) {
    controller.current_room.removeClass("element-selected");

    // Remove other popup menus.
    $(".room-menu").remove();

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

    // Remove other popup menus.
    $(".room-menu").remove();
    $(".exit-menu").remove();
    if (this.current_path) {
        this.current_path.setAttribute("stroke", "#666");
        this.current_path = null;
    }

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
    this.mode = "";

    this.finishDraggingPath();

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Drop a room.
 */
MapEditor.prototype.dropRoom = function(event) {
    this.mode = "";

    // Show room menu.
    var menu = $(".room-menu");

    var room_key = this.current_room.data("key");
    var room = controller.rooms[room_key];
    var width = menu.width();
    menu.css({
        "left": room.x - width / 2,
        "top": room.y + controller.room_size,
        "position": "absolute"
    });
    menu.show();

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Click the background to unselect all room.
 */
MapEditor.prototype.containerMouseUp = function(event) {
    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();
    $(".exit-menu").remove();
    if (this.current_path) {
        this.current_path.setAttribute("stroke", "#666");
        this.current_path = null;
    }
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
    var room = controller.rooms[room_key];

    var menu = $("<div>")
        .addClass("element-menu room-menu");

    // title
    $("<div>")
        .addClass("menu-room-name")
        .text(room.info.name)
        .appendTo(menu);

    $("<div>")
        .addClass("menu-room-key")
        .text(room.info.key)
        .appendTo(menu);

    $("<div>")
        .addClass("menu-room-typeclass")
        .text("(" + room.info.typeclass + ")")
        .appendTo(menu);

    var button_bar = $("<div>")
        .addClass("room-button-bar")
        .appendTo(menu);

    // delete button
    var button = $("<button>")
        .addClass("btn btn-default room-menu-button")
        .attr("type", "button")
        .data("key", room.info.key)
        .on("mouseup", this.onDeleteRoom)
        .appendTo(button_bar);

    var icon = $("<span>")
        .addClass("glyphicon glyphicon-trash")
        .appendTo(button);

    // edit button
    var button = $("<button>")
        .addClass("btn btn-default room-menu-button")
        .attr("type", "button")
        .data("key", room.info.key)
        .on("mouseup", this.onEditRoom)
        .appendTo(button_bar);

    var icon = $("<span>")
        .addClass("glyphicon glyphicon-edit")
        .appendTo(button);

    menu.appendTo($("#container"));

    var width = menu.width();
    menu.css({
        "left": room.x - width / 2,
        "top": room.y + controller.room_size,
        "position": "absolute"
    });
}


/*
 * Display a path's menu.
 */
MapEditor.prototype.showPathMenu = function(path_id) {
    var path_info = this.paths[path_id];

    // Stroke the path.
    this.current_path = document.getElementById(path_id);
    this.current_path.setAttribute("stroke", "#e30");

    var x = (path_info.x1 + path_info.x2) / 2;
    var y = (path_info.y1 + path_info.y2) / 2;

    var menu = $("<div>")
        .addClass("element-menu exit-menu");

    for (var key in path_info.exits) {
        var exit = path_info.exits[key];

        var menu_item = $("<div>")
            .addClass("menu-item exit-menu-item");

        var name = $("<div>")
            .addClass("menu-exit-key")
            .text(exit.key + " (" + exit.typeclass + ")")
            .appendTo(menu_item);

        var source_room = this.rooms[exit.location];
        var target_room = this.rooms[exit.destination];
        var source_name = source_room.info.name? source_room.info.name: source_room.info.key;
        var target_name = target_room.info.name? target_room.info.name: target_room.info.key;
        var direction = source_name + " > " + target_name;
        var name = $("<div>")
            .addClass("menu-exit-direction")
            .text(direction)
            .appendTo(menu_item);

        var button_bar = $("<div>")
            .addClass("exit-button-bar")
            .appendTo(menu_item);

        // delete button
        var button = $("<button>")
            .addClass("btn btn-default btn-sm exit-menu-button")
            .attr("type", "button")
            .data("path", path_id)
            .data("exit", exit.key)
            .on("mouseup", this.onDeleteExit)
            .appendTo(button_bar);

        var icon = $("<span>")
            .addClass("glyphicon glyphicon-trash")
            .appendTo(button);

        // edit button
        var button = $("<button>")
            .addClass("btn btn-default btn-sm exit-menu-button")
            .attr("type", "button")
            .data("path", path_id)
            .data("exit", exit.key)
            .on("mouseup", this.onEditExit)
            .appendTo(button_bar);

        var icon = $("<span>")
            .addClass("glyphicon glyphicon-edit")
            .appendTo(button);

        menu_item.appendTo(menu);
    }

    menu.appendTo($("#container"));

    var width = menu.width();
    menu.css({
        "left": x - width / 2,
        "top": y,
        "position": "absolute"
    });
}


/*
 * On click the button to edit a room.
 */
MapEditor.prototype.onEditRoom = function(event) {
    var context = {
        key: $(this).data("key")
    }
    controller.saveMapPositions(controller.saveForEditRoom, context);

    // Prevent the container's event.
    event.stopPropagation();
}


MapEditor.prototype.saveForEditRoom = function(data, context) {
    var room_key = context.key;
    window.parent.controller.editObject(controller.room_typeclass, room_key);

    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();
}

/*
 * On click the button to delete a room.
 */
MapEditor.prototype.onDeleteRoom = function(event) {
    var room_key = $(this).data("key");
    window.parent.controller.confirm("",
                                     "Delete this room?",
                                     controller.confirmDeleteRoom,
                                     {key: room_key});

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Delete the room.
 */
MapEditor.prototype.confirmDeleteRoom = function(e) {
    window.parent.controller.hideWaiting();

    var room_key = e.data.key;
    var objects = [room_key];

    // Get all relative exits.
    var exits = [];
    for (var path_id in controller.rooms[room_key].paths) {
        exits = exits.concat(Object.keys(controller.paths[path_id].exits));
    }
    objects = objects.concat(exits);

    var context = {
        room: room_key,
        exits: exits
    }
    service.deleteObjects(objects, controller.deleteRoomSuccess, controller.failedCallback, context);
}


/*
 * Delete the room success..
 */
MapEditor.prototype.deleteRoomSuccess = function(data, context) {
    // Remove popup menus.
    $(".room-menu").remove();

    var room_key = context.room;

    // Remove relative paths.
    for (var path_id in controller.rooms[room_key].paths) {
        var path = document.getElementById(path_id);
        path.parentNode.removeChild(path);

        var room1 = controller.paths[path_id].room1;
        var room2 = controller.paths[path_id].room2;

        if (room1 != room_key) {
            delete controller.rooms[room1].paths[path_id];
        }
        else {
            delete controller.rooms[room2].paths[path_id];
        }

        delete controller.paths[path_id];
    }

    // Remove the room.
    $("#room-" + room_key).remove();
    $("#roomname-" + room_key).remove();
    delete controller.rooms[room_key];
}


/*
 * On click the button to edit an exit.
 */
MapEditor.prototype.onEditExit = function(event) {
    var context = {
        path: $(this).data("path"),
        key: $(this).data("exit")
    }
    controller.saveMapPositions(controller.saveForEditExit, context);

    // Prevent the container's event.
    event.stopPropagation();
}


MapEditor.prototype.saveForEditExit = function(data, context) {
    var exit_key = context.key;
    window.parent.controller.editObject(controller.exit_typeclass, exit_key);

    // Remove popup menus.
    $(".exit-menu").remove();

    var path = document.getElementById(path_id);
    path.setAttribute("stroke", "#666");
}


/*
 * On click the button to delete an exit.
 */
MapEditor.prototype.onDeleteExit = function(event) {
    var path_id = $(this).data("path");
    var exit_key = $(this).data("exit");
    window.parent.controller.confirm("",
                                     "Delete this exit?",
                                     controller.confirmDeleteExit,
                                     {path: path_id,
                                      exit: exit_key});

    // Prevent the container's event.
    event.stopPropagation();
}


/*
 * Delete the exit.
 */
MapEditor.prototype.confirmDeleteExit = function(e) {
    window.parent.controller.hideWaiting();

    var context = e.data;
    service.deleteObject(e.data.exit,
                         controller.exit_typeclass,
                         controller.deleteExitSuccess,
                         controller.failedCallback,
                         context);
}


/*
 * Delete the exit success..
 */
MapEditor.prototype.deleteExitSuccess = function(data, context) {
    var path_id = context.path;
    var exit_key = context.exit;
    delete controller.paths[path_id].exits[exit_key];

    // Remove the old menu.
    $(".exit-menu").remove();

    // If all exits have been removed.
    if (Object.keys(controller.paths[path_id].exits).length == 0) {
        // Remove the path.
        delete controller.paths[path_id];
        var path = document.getElementById(path_id);
        path.parentNode.removeChild(path);
    }
    else {
        // Refresh the path menu.
        controller.showPathMenu(path_id);
    }
}


MapEditor.prototype.refresh = function() {
    if (this.area_key) {
        service.queryMap(this.area_key, this.queryMapSuccess, this.failedCallback);
    }
    else {
        service.addArea(this.area_typeclass,
                        this.default_map_width,
                        this.default_map_height,
                        this.addAreaSuccess,
                        this.addAreaFailed);
    }
}


/*
 * Query the map's data success.
 */
MapEditor.prototype.queryMapSuccess = function(data) {
    // Clear map.
    $("#container>.element-room").remove();
    $("#container>.element-room-name").remove();
    var svg = document.getElementById("map-svg");
    svg.innerHTML = "";

    if (!controller.origin_map) {
        controller.origin_map = data;
    }

    controller.background = "";
    controller.rooms = {};
    controller.paths = {};

    // Draw the background.

    /*
    var map_scale = 1;
    var map_room_size = 40;
    var original_point_x = 0;
    var original_point_y = 0;
    */

    // area
    controller.background = data.area.background;

    /*
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
    */

    if (controller.background) {
        controller.area_width = data.area.width || 0;
        controller.area_height = data.area.height || 0;
        $("#map-image")
            .attr("src", CONFIG.resource_url + controller.background);
    }
    else {
        controller.area_width = data.area.width || controller.default_map_width;
        controller.area_height = data.area.height || controller.default_map_height;
        $("#map-image")
            .attr("src", controller.blank_map);

    }

    // rooms
    for (var i = 0; i < data.rooms.length; i++) {
        var room_info = data.rooms[i];

        var x = 0;
        var y = 0;
        if (room_info.position) {
            x = room_info.position[0];
            y = room_info.position[1];
            //x = original_point_x + room_info.position[0] * map_scale;
            //y = original_point_y - room_info.position[1] * map_scale;
        }
        else {
            x = controller.area_width / 2;
            y = controller.area_height / 2;
        }
        controller.createRoom(room_info, x, y);
    }

    // exits
    for (var i = 0; i < data.exits.length; i++) {
        var exit_info = data.exits[i];

        if (!(exit_info.location in controller.rooms)) {
        }
        else if (!(exit_info.destination in controller.rooms)) {
        }
        else {
            controller.createPath(exit_info);
        }
    }
}


/*
 * Save the new area success
 */
MapEditor.prototype.addAreaSuccess = function(data) {
    controller.area_key = data.key;
    var width = data.width || 0;
    var height = data.height || 0;

    controller.setBackgroundSize(width, height);
}


/*
 * Save the new area failed.
 */
MapEditor.prototype.addAreaFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message, newMapFailedNotified);
}


MapEditor.prototype.newMapFailedNotified = function(code, message, data) {
    window.parent.controller.hideWaiting();
    controller.exitNoChange();
}


/*
 * Save the map.
 */
MapEditor.prototype.saveMapPositions = function(successCallback, context) {
    var area = {
        key: this.area_key,
        background: this.background,
        width: this.area_width,
        height: this.area_height
    }

    var rooms = [];
    for (var key in controller.rooms) {
        var room_info = controller.rooms[key];
        rooms.push({
            key: key,
            position: [room_info.x, room_info.y]
        });
    }

    service.saveMapPositions(area, rooms, successCallback, this.failedCallback, context);
}


/*
 * Discard all changes.
 */
MapEditor.prototype.confirmDiscard = function(e) {
    window.parent.controller.hideWaiting();

    // Remove added objects.
    // rooms
    var origin_rooms = [];
    for (var i = 0; i < controller.origin_map.rooms.length; i++) {
        var room_info = controller.origin_map.rooms[i];
        origin_rooms[room_info.key] = null;
    }

    var objects = []
    for (var room_key in controller.rooms) {
        if (!(room_key in origin_rooms)) {
            objects.push(room_key);
        }
    }

    // exits
    var origin_exits = [];
    for (var i = 0; i < controller.origin_map.exits.length; i++) {
        var exit_info = controller.origin_map.exits[i];
        origin_exits[exit_info.key] = null;
    }

    for (var path_id in controller.paths) {
        for (var exit_key in controller.paths[path_id].exits) {
            if (!(exit_key in origin_exits)) {
                objects.push(exit_key);
            }
        }
    }
    service.deleteObjects(objects, controller.removeAddedObjectsSuccess, controller.failedCallback);
}


/*
 * Remove added objects success. Restore positions.
 */
MapEditor.prototype.removeAddedObjectsSuccess = function(data) {
    var map = controller.origin_map;

    var area = {
        key: map.area.key,
        background: map.area.background,
        width: map.area.width,
        height: map.area.height
    }

    var rooms = [];
    for (var i = 0; i < map.rooms.length; i++) {
        var room_info = map.rooms[i];
        if (!(room_info.key in controller.rooms)) {
            // Could not restore deleted objects.
            continue;
        }

        rooms.push({
            key: room_info.key,
            position: room_info.position
        });
    }

    // Save the original map.
    service.saveMapPositions(area, rooms, controller.discardMapSuccess, controller.failedCallback);
}


/*
 * Remove added objects success.
 */
MapEditor.prototype.discardMapSuccess = function(data) {
    controller.exit();
}


/*
 * Discard all changes success.
 */
MapEditor.prototype.discardMapSuccess = function(data) {
    controller.exit();
}


MapEditor.prototype.exit = function() {
    setInterval(function() {window.parent.controller.popPage(true);}, 0);
}

MapEditor.prototype.exitNoChange = function() {
    setInterval(function() {window.parent.controller.popPage(false);}, 0);
}