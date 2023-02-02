
/*
 * Derive from the base class.
 */
FlowEditor = function() {
    this.box_width = 120;
    this.box_height = 40;
    this.path_color = "#666";

    this.path_index = 0;

    this.current_box = null;
    this.box_offset_x = 0;
    this.box_offset_y = 0;
    this.current_path = null;
    this.mode = "";

    // All rooms and paths.
    this.boxes = {};
    this.paths = {};

    // Flow changed.
    this.changed = false;
}

FlowEditor.prototype.init = function() {
    this.flow_key = utils.getQueryString("flow");

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");

    this.bindEvents();
    this.refresh();
}

FlowEditor.prototype.bindEvents = function() {
    $("#exit-button").on("click", this.onExit);
    $("#save-record").on("click", this.onSave);

    // Mouse down on a box.
    $("#container").on("mousedown", ".element-room", this.onBoxMouseDown);

    // Mouse move on the container.
    $("#container").on("mousemove", this.onMouseMove);

    // Mouse up on a box.
    $("#container").on("mouseup", ".element-room", this.onBoxMouseUp);

    // Mouse up on the container.
    $("#container").on("mouseup", this.onContainerMouseUp);
}

FlowEditor.prototype.onExit = function() {
    if (!controller.changed) {
        controller.exitNoChange();
    }
    else {
        window.parent.controller.confirm("",
                                         "Discard changes? (Deleted objects and saved attributes can not be restored.)",
                                         controller.confirmDiscard);
    }
}

FlowEditor.prototype.onSave = function() {
    controller.saveFlowPositions(controller.saveForExit);
}

FlowEditor.prototype.saveForExit = function(data) {
    controller.exit();
}

/*
 * Common failed callback.
 */
FlowEditor.prototype.failedCallback = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);
}


/***********************************
 *
 * Draw map.
 *
 ***********************************/

/*
 * Create a new box.
 */
FlowEditor.prototype.createBox = function(info, x, y) {
    this.boxes[info.key] = {
        info: info,
        x: x,
        y: y,
        paths: {}
    }

    var box = $("<div>")
        .attr("id", "box-" + info.key)
        .data("key", info.key)
        .addClass("element-box")
        .appendTo($("#container"));

    box.css({
        "left": x - box.outerWidth() / 2,
        "top": y - box.outerHeight() / 2,
        "position": "absolute"
    });

    if (info.name) {
        var name = $("<div>")
            .attr("id", "boxname-" + info.key)
            .addClass("element-box-name")
            .text(info.name)
            .appendTo($("#container"));

        var width = name.width();

        name.css({
            "left": x - name.width() / 2,
            "top": y - name.height() / 2,
            "position": "absolute"});
    }
}

/*
 * Create a path.
 */
FlowEditor.prototype.createPath = function(info) {
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
    // Draw a line from the source box to the target box.
    var source_box = controller.boxes[info.location];
    var x1 = source_box.x;
    var y1 = source_box.y;

    var target_box = controller.boxes[info.destination];
    var x2 = target_box.x;
    var y2 = target_box.y;

    var svg = document.getElementById("map-svg");
    var namespace = "http://www.w3.org/2000/svg";
    var path = document.createElementNS(namespace, "path");
    path.setAttribute("id", path_id);
    path.setAttribute("stroke", this.path_color);
    path.setAttribute("stroke-width", "5");
    path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
    path.addEventListener("click", this.onPathClick);
    svg.appendChild(path);

    // Add records.
    this.paths[path_id] = {
        box1: info.location,
        box2: info.destination,
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2,
        exits: {}
    }
    this.paths[path_id].exits[info.key] = info;

    this.boxes[info.location].paths[path_id] = "";
    this.boxes[info.destination].paths[path_id] = "";
}

/***********************************
 *
 * Mouse down event.
 *
 ***********************************/

/*
 * On mouse down on a box.
 */
FlowEditor.prototype.onBoxMouseDown = function(event) {
    if ($(this).hasClass("new-element")) {
        // On a new box.
        controller.newBoxMouseDown(event);
    }
    else if ($(this).hasClass("element-selected")) {
        // On a selected box.
        controller.selectedBoxMouseDown(event);
    }
    else {
        // On an unselected box.
        controller.unselectedBoxMouseDown(event);
    }
}

/*
 * Mouse down on a new box.
 */
FlowEditor.prototype.newBoxMouseDown = function(event) {
    // Drag the box.
    var container = $("#container");
    this.mode = "NEW_BOX";

    var target = $(event.currentTarget);

    this.box_offset_x = event.clientX - target.offset().left;
    this.box_offset_y = event.clientY - target.offset().top;
    this.current_box = target.clone();
    this.current_box.appendTo(container);

    this.newBoxMouseMove(event);
}

/*
 * Mouse down on a selected box.
 */
FlowEditor.prototype.selectedBoxMouseDown = function(event) {
    // Select a box.
    this.mode = "SELECTED_BOX";
    this.current_box = $(event.currentTarget);
    this.box_offset_x = event.clientX - this.current_box.offset().left;
    this.box_offset_y = event.clientY - this.current_box.offset().top;
}

/*
 * Mouse down on an unselected box.
 */
FlowEditor.prototype.unselectedBoxMouseDown = function(event) {
    this.mode = "UNSELECTED_BOX";
    this.current_box = $(event.currentTarget);
    this.box_offset_x = event.clientX - this.current_box.offset().left;
    this.box_offset_y = event.clientY - this.current_box.offset().top;
}


/***********************************
 *
 * Mouse move event.
 *
 ***********************************/

/*
 * Mouse move on the container.
 */
FlowEditor.prototype.onMouseMove = function(event) {
    if (controller.mode == "") {
        return;
    }

    if (controller.mode == "NEW_BOX") {
        // Move a new box.
        controller.newBoxMouseMove(event);
    }
    else if (controller.mode == "SELECTED_BOX") {
        // Move on a selected box.
        // controller.selectedBoxMouseMove(event);
    }
    else if (controller.mode == "UNSELECTED_BOX") {
        // Move on an unselected box.
        controller.unselectedBoxMouseMove(event);
    }
    else if (controller.mode == "DRAG_PATH") {
        // Drag a new path.
        controller.dragPath(event);
    }
    else if (controller.mode == "DRAG_BOX") {
        // Drag a box.
        controller.dragBox(event);
    }
}

/*
 * Move a new box.
 */
FlowEditor.prototype.newBoxMouseMove = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    // Set to grids.
    var box_x = x - this.box_offset_x;
    var box_y = y - this.box_offset_y;

    // Move the box.
    controller.current_box.css({
        "left": box_x,
        "top": box_y,
        "position": "absolute"
    });
}

/*
 * Move an unselected box.
 */
FlowEditor.prototype.unselectedBoxMouseMove = function(event) {
    if (event.originalEvent.movementX == 0 && event.originalEvent.movementY == 0) {
        // No movement.
        return;
    }

    // Drag the room or drag a new path.
    var width = controller.current_box.innerWidth();
    var height = controller.current_box.innerHeight();
    var relative_x = controller.box_offset_x - controller.current_box.outerWidth() / 2;
    var relative_y = controller.box_offset_y - controller.current_box.outerHeight() / 2;

    if (Math.abs(relative_x) - width / 2　< 0 &&
        Math.abs(relative_y) - height / 2　< 0) {
        this.mode = "DRAG_BOX";
        controller.changed = true;
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
FlowEditor.prototype.dragPath = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    var x1 = controller.current_box.position().left + controller.current_box.outerWidth() / 2;
    var y1 = controller.current_box.position().top + controller.current_box.outerHeight() / 2;
    var x2 = x;
    var y2 = y;

    this.current_path.setAttribute("d", "M " + x1 + " " + y1 + " L " + x2 + " " + y2);
}


/*
 * Drag a box.
 */
FlowEditor.prototype.dragBox = function(event) {
    var container = $("#container");
    var x = event.clientX - container.offset().left;
    var y = event.clientY - container.offset().top;

    var width = this.current_box.outerWidth();
    var height = this.current_box.outerHeight();

    var box_x = x - this.box_offset_x + width / 2;
    var box_y = y - this.box_offset_y + height / 2;

    // Move the box.
    controller.current_box.css({
        "left": box_x - width / 2,
        "top": box_y - height / 2,
        "position": "absolute"});

    // Move the box's name.
    var box_key = this.current_box.data("key");
    var name = $("#boxname-" + box_key);
    if (name) {
        name.css({
            "left": room_x - name.width() / 2,
            "top": room_y - name.height() / 2,
            "position": "absolute"
        });
    }

    this.boxes[box_key].x = box_x;
    this.boxes[box_key].y = box_y;

    // Move linked paths.
    for (var path_id in this.boxes[box_key].paths) {
        var path_info = this.paths[path_id];
        var x1 = path_info.x1;
        var y1 = path_info.y1;
        var x2 = path_info.x2;
        var y2 = path_info.y2;

        if (room_key == path_info.box1) {
            x1 = box_x;
            y1 = box_y;

            this.paths[path_id]["x1"] = box_x;
            this.paths[path_id]["y1"] = box_y;
        }
        else if (room_key == path_info.box2) {
            x2 = box_x;
            y2 = box_y;

            this.paths[path_id]["x2"] = box_x;
            this.paths[path_id]["y2"] = box_y;
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
 * On mouse up on a box.
 */
FlowEditor.prototype.onBoxMouseUp = function(event) {
    if (controller.mode == "DRAG_PATH") {
        // Drop the new path.
        controller.dropPathOnRoom(event);
    }
}


/*
 * Drop the new path on a room.
 */
MapEditor.prototype.dropPathOnRoom = function(event) {
    event.stopPropagation();

    this.mode = "";

    if ($(event.currentTarget).hasClass("new-element")) {
        // Can not draw a path to new element buttons.
        controller.finishDraggingPath();
        return;
    }

    var source_key = this.current_box.data("key");
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
    var exit_info_1 = {
        element_type: this.exit_element_type,
        location: source_key,
        destination: target_key
    };
    service.addExit(
        this.exit_element_type,
        source_key,
        target_key,
        function(data) {
            controller.addExitSuccess(data, exit_info_1);
        },
        this.addExitFailed
    );

    if (new_path) {
        // Add a reverse exit.
        var exit_info_2 = {
            element_type: this.exit_element_type,
            location: target_key,
            destination: source_key
        };
        service.addExit(
            this.exit_element_type,
            target_key,
            source_key,
            function(data) {
                controller.addExitSuccess(data, exit_info_2);
            },
            this.addExitFailed
        );
    }
}


MapEditor.prototype.addExitSuccess = function(data, exit_info) {
    controller.changed = true;
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
    else if (controller.mode == "DRAG_BOX") {
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
    var x = this.current_box.position().left + this.current_box.outerWidth() / 2;
    var y = this.current_box.position().top + this.current_box.outerHeight() / 2;

    // Set to grids.
    if (this.use_grid) {
        x = Math.round(x / this.grid_size) * this.grid_size;
        y = Math.round(y / this.grid_size) * this.grid_size;
    }
    service.addRoom(this.room_element_type, this.area_key, [x, y], this.addRoomSuccess, this.addRoomFailed);
}


MapEditor.prototype.addRoomSuccess = function(data) {
    controller.changed = true;

    var room_key = data.key;

    var x = controller.current_box.position().left + controller.current_box.outerWidth() / 2;
    var y = controller.current_box.position().top + controller.current_box.outerHeight() / 2;

    var room_info = {
        key: room_key,
        name: "",
        element_type: controller.room_element_type,
        position: [x, y]
    }
    controller.createRoom(room_info, x, y);

    controller.current_box.remove()
    controller.current_box = null;
    controller.mode = "";
}


MapEditor.prototype.addRoomFailed = function(code, message, data) {
    window.parent.controller.notify("ERROR", code + ": " + message);

    this.current_box.remove()
    this.current_box = null;
    this.mode = "";
}


/*
 * Unselect the room.
 */
MapEditor.prototype.selectedRoomMouseUp = function(event) {
    controller.current_box.removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();
    $(".room-exits").remove();

    this.current_box = null;
    this.mode = "";
}


/*
 * Select the room.
 */
MapEditor.prototype.unselectedRoomMouseUp = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    // Unselect other rooms.
    $(".element-room").removeClass("element-selected");

    // Select this room.
    this.current_box.addClass("element-selected");

    // Remove other popup menus.
    $(".room-menu").remove();
    $(".exit-menu").remove();
    if (this.current_path) {
        this.current_path.setAttribute("stroke", this.path_color);
        this.current_path = null;
    }

    // Show this room's menu.
    var room_key = this.current_box.data("key");
    this.showRoomMenu(room_key);

    this.current_box = null;
    this.mode = "";
}


/*
 * Drop a new path.
 */
MapEditor.prototype.dropPath = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    this.mode = "";
    this.finishDraggingPath();
}


/*
 * Drop a room.
 */
MapEditor.prototype.dropRoom = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    controller.changed = true;

    this.mode = "";

    // Show room menu.
    var menu = $(".room-menu");

    var room_key = this.current_box.data("key");
    var room = controller.rooms[room_key];
    var width = menu.width();
    menu.css({
        "left": room.x - width / 2,
        "top": room.y + controller.room_size,
        "position": "absolute"
    });
    menu.show();
}


/*
 * Click the background to unselect all room.
 */
MapEditor.prototype.containerMouseUp = function(event) {
    if ($(".room-exits").length > 0) {
        // Remove room exits menu and show room's menu.
        $(".room-exits").remove();
        $(".room-menu").show();
    }
    else {
        // Unselect all rooms.
        $(".element-room").removeClass("element-selected");

        // Remove popup menus.
        $(".room-menu").remove();
        $(".exit-menu").remove();
    }

    if (this.current_path) {
        this.current_path.setAttribute("stroke", this.path_color);
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
        .addClass("menu-room-type")
        .text("(" + room.info.element_type + ")")
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

    // add exit button
    var button = $("<button>")
        .addClass("btn btn-default room-menu-button")
        .attr("type", "button")
        .data("key", room.info.key)
        .on("mouseup", this.onRoomExits)
        .appendTo(button_bar);

    var icon = $("<span>")
        .addClass("glyphicon glyphicon-transfer")
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
            .text(exit.key + " (" + exit.element_type + ")")
            .appendTo(menu_item);

        var source_name = "";
        if (exit.location in this.rooms && this.rooms[exit.location].info.name) {
            source_name = this.rooms[exit.location].info.name;
        }
        else {
            source_name = exit.location;
        }

        var target_name = "";
        if (exit.destination in this.rooms && this.rooms[exit.destination].info.name) {
            target_name = this.rooms[exit.destination].info.name;
        }
        else {
            target_name = exit.destination;
        }

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
    // Prevent the container's event.
    event.stopPropagation();

    var context = {
        key: $(this).data("key")
    }
    controller.saveMapPositions(controller.saveForEditRoom, context);
}


MapEditor.prototype.saveForEditRoom = function(data, context) {
    controller.changed = true;

    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();

    var room_key = context.key;
    window.parent.controller.editMatter(controller.room_element_type, room_key);
}

/*
 * On click the button to delete a room.
 */
MapEditor.prototype.onDeleteRoom = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    var room_key = $(this).data("key");
    window.parent.controller.confirm("",
                                     "Delete this room?",
                                     controller.confirmDeleteRoom,
                                     {key: room_key});
}


/*
 * Delete the room.
 */
MapEditor.prototype.confirmDeleteRoom = function(e) {
    window.parent.controller.hideWaiting();

    var room_key = e.data.key;
    var to_delete = {};
    to_delete[controller.room_element_type] = room_key;

    // Get all relative exits.
    var exits = [];
    for (var path_id in controller.rooms[room_key].paths) {
        exits = exits.concat(Object.keys(controller.paths[path_id].exits));
    }
    to_delete[controller.exit_element_type] = exits;

    service.deleteElements(to_delete, function(data) {
        controller.deleteRoomSuccess(data, room_key);
    }, controller.failedCallback);
}


/*
 * Delete the room success..
 */
MapEditor.prototype.deleteRoomSuccess = function(data, room_key) {
    controller.changed = true;

    // Remove popup menus.
    $(".room-menu").remove();

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
 * Show a room's exits.
 */
MapEditor.prototype.onRoomExits = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    var room_key = $(this).data("key");

    // Hide room's menu
    $(".room-menu").hide();

    // Show exits menu.
    var menu = $("<div>")
        .addClass("element-menu exit-menu room-exits");

    // Add a header and create exit button.
    var menu_item = $("<div>")
        .addClass("menu-item exit-menu-item exit-menu-header")
        .appendTo(menu);

    // add button
    var button = $("<button>")
        .addClass("btn btn-default btn-sm exit-menu-button button-right")
        .attr("type", "button")
        .data("room", room_key)
        .on("mouseup", controller.onCreateExit)
        .appendTo(menu_item);

    var icon = $("<span>")
        .addClass("glyphicon glyphicon-plus")
        .appendTo(button);

    for (var path_id in controller.paths) {
        var path_info = controller.paths[path_id];
        if (path_info.room1 == room_key || path_info.room2 == room_key) {
            for (var key in path_info.exits) {
                var exit = path_info.exits[key];

                var menu_item = $("<div>")
                    .addClass("menu-item exit-menu-item");

                var name = $("<div>")
                    .addClass("menu-exit-key")
                    .text(exit.key + " (" + exit.element_type + ")")
                    .appendTo(menu_item);

                var source_name = "";
                if (exit.location in controller.rooms && controller.rooms[exit.location].info.name) {
                    source_name = controller.rooms[exit.location].info.name;
                }
                else {
                    source_name = exit.location;
                }

                var target_name = "";
                if (exit.destination in controller.rooms && controller.rooms[exit.destination].info.name) {
                    target_name = controller.rooms[exit.destination].info.name;
                }
                else {
                    target_name = exit.destination;
                }

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
                    .on("mouseup", controller.onDeleteExit)
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
                    .on("mouseup", controller.onEditExit)
                    .appendTo(button_bar);

                var icon = $("<span>")
                    .addClass("glyphicon glyphicon-edit")
                    .appendTo(button);

                menu_item.appendTo(menu);
            }
        }
    }

    menu.appendTo($("#container"));

    var room = controller.rooms[room_key];
    var width = menu.width();
    menu.css({
        "left": room.x - width / 2,
        "top": room.y + controller.room_size,
        "position": "absolute"
    });
}


/*
 * Create a new exit.
 */
MapEditor.prototype.onCreateExit = function(event) {
    var context = {
        room: $(this).data("room")
    }
    controller.saveMapPositions(controller.saveForCreateExit, context);
}


MapEditor.prototype.saveForCreateExit = function(data, context) {
    controller.changed = true;

    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();

    var values = {
        location: context.room
    }
    window.parent.controller.createMatter(controller.exit_element_type, controller.exit_element_type, values);
}


/*
 * On click the button to edit an exit.
 */
MapEditor.prototype.onEditExit = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    var context = {
        path: $(this).data("path"),
        key: $(this).data("exit")
    }
    controller.saveMapPositions(controller.saveForEditExit, context);
}


MapEditor.prototype.saveForEditExit = function(data, context) {
    controller.changed = true;

    var exit_key = context.key;
    window.parent.controller.editMatter(controller.exit_element_type, exit_key);

    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove popup menus.
    $(".room-menu").remove();
    $(".exit-menu").remove();

    // Unselect the path.
    if (controller.current_path) {
        controller.current_path.setAttribute("stroke", controller.path_color);
        controller.current_path = null;
    }
}


/*
 * On click the button to delete an exit.
 */
MapEditor.prototype.onDeleteExit = function(event) {
    // Prevent the container's event.
    event.stopPropagation();

    var path_id = $(this).data("path");
    var exit_key = $(this).data("exit");
    window.parent.controller.confirm(
        "",
        "Delete this exit?",
        controller.confirmDeleteExit,
        {
            path: path_id,
            exit: exit_key,
        }
    );
}


/*
 * Delete the exit.
 */
MapEditor.prototype.confirmDeleteExit = function(e) {
    window.parent.controller.hideWaiting();

    var exit_info = e.data;
    service.deleteElement(
        e.data.exit,
        controller.exit_element_type,
        function(data) {
            controller.deleteExitSuccess(data, exit_info);
        },
        controller.failedCallback
    );
}


/*
 * Delete the exit success.
 * Used by both room menu's delete exit and exit menu's delete exit.
 */
MapEditor.prototype.deleteExitSuccess = function(data, exit_info) {
    controller.changed = true;

    var path_id = exit_info.path;
    var exit_key = exit_info.exit;
    delete controller.paths[path_id].exits[exit_key];

    // Unselect all rooms.
    $(".element-room").removeClass("element-selected");

    // Remove the old menu.
    $(".room-menu").remove();
    $(".exit-menu").remove();

    // If all exits have been removed.
    if (Object.keys(controller.paths[path_id].exits).length == 0) {
        // Remove the path.
        var path_info = controller.paths[path_id];
        if (path_info.room1 in controller.rooms) {
            delete controller.rooms[path_info.room1].paths[path_id];
        }
        if (path_info.room2 in controller.rooms) {
            delete controller.rooms[path_info.room2].paths[path_id];
        }
        delete controller.paths[path_id];

        var path = document.getElementById(path_id);
        path.parentNode.removeChild(path);
    }
    else {
        // Refresh the path menu.
        // controller.showPathMenu(path_id);

        // Unselect the path.
        if (controller.current_path) {
            controller.current_path.setAttribute("stroke", controller.path_color);
            controller.current_path = null;
        }
    }
}


FlowEditor.prototype.refresh = function(param) {
    if (this.flow_key) {
        service.queryQuestsChain(this.flow_key, this.queryFlowSuccess, this.failedCallback);
    }
    else {
        /*
        service.addArea(
            this.area_element_type,
            this.default_map_width,
            this.default_map_height,
            this.addAreaSuccess,
            this.addAreaFailed,
        );
        */
    }
}


/*
 * Query the flow's data success.
 */
FlowEditor.prototype.queryFlowSuccess = function(data) {
    // Clear map.
    $("#container>.element-box").remove();
    $("#container>.element-box-name").remove();
    var svg = document.getElementById("map-svg");
    svg.innerHTML = "";

    if (!controller.origin_flow) {
        controller.origin_flow = data;
    }

    controller.boxes = {};
    controller.paths = {};

    // heads
    for (var i = 0; i < data.heads.length; i++) {
        var box_info = data.nodes[heads[i]];

        var x = box_width * i + box_width / 2 + 20;
        var y = box_height / 2 + 20;
        controller.createBox(box_info, x, y);

        for (var j = 0; j < box_info.nexts.length; j++) {
            var next_box_info = data.nodes[box_info.nexts[j]];
            controller.drawNextBox(box_info, next_box_info);
        }

        /*
        // exits
        for (var i = 0; i < data.exits.length; i++) {
            var exit_info = data.exits[i];

            if (!(exit_info.location in controller.rooms)) {
                controller.createOuterPath(exit_info);
            }
            else if (!(exit_info.destination in controller.rooms)) {
                controller.createOuterPath(exit_info);
            }
            else {
                controller.createPath(exit_info);
            }
        }
        */
    }

    window.parent.controller.setFrameSize();
}

FlowEditor.prototype.drawNextBox(from_box, to_box) {

}


/*
 * Save the new area success
 */
MapEditor.prototype.addAreaSuccess = function(data) {
    controller.changed = true;

    controller.area_key = data.key;

    // Show the map's name.
    var name = data.name? data.name: "";
    var key = data.key? data.key: "";
    $("#form-name").text(name + "(" + key + ")");

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

    service.saveMapPositions(
        area,
        rooms,
        function(data) {
            successCallback(data, context);
        },
        this.failedCallback
    );
}


/*
 * Discard all changes.
 */
MapEditor.prototype.confirmDiscard = function(e) {
    window.parent.controller.hideWaiting();

    // Remove added objects.
    var to_delete = []

    // rooms
    var origin_rooms = [];
    if (controller.origin_map) {
        for (var i = 0; i < controller.origin_map.rooms.length; i++) {
            var room_info = controller.origin_map.rooms[i];
            origin_rooms[room_info.key] = null;
        }
    }

    var rooms_to_delete = [];
    for (var room_key in controller.rooms) {
        if (!(room_key in origin_rooms)) {
            rooms_to_delete.push(room_key);
        }
    }
    to_delete[controller.room_element_type] = rooms_to_delete;

    // exits
    var origin_exits = [];
    if (controller.origin_map) {
        for (var i = 0; i < controller.origin_map.exits.length; i++) {
            var exit_info = controller.origin_map.exits[i];
            origin_exits[exit_info.key] = null;
        }
    }

    var exits_to_delete = [];
    for (var path_id in controller.paths) {
        for (var exit_key in controller.paths[path_id].exits) {
            if (!(exit_key in origin_exits)) {
                exits_to_delete.push(exit_key);
            }
        }
    }
    to_delete[controller.exit_element_type] = exits_to_delete;

    // area
    if (!controller.origin_map) {
        // It's a new map. Delete the area.
        to_delete[controller.area_element_type] = controller.area_key;
    }

    service.deleteElements(to_delete, controller.removeAddedObjectsSuccess, controller.failedCallback);
}


/*
 * Remove added objects success. Restore positions.
 */
MapEditor.prototype.removeAddedObjectsSuccess = function(data) {
    if (!controller.origin_map) {
        controller.exit();
    }
    else {
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