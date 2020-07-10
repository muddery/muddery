
field_creator = {
    createControlGroup: function(name, ctrl, label, help_text) {
        var group = $("<div>")
            .addClass("control-group")
            .addClass("control-item-" + name);

        // label
        var label_div = $("<label>")
            .addClass("control-label")
            .text(label)
            .appendTo(group);
        
        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        ctrl.appendTo(ctrl_div);

        $("<p>")
            .addClass("help-block")
            .text(help_text)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("message-block")
            .hide()
            .appendTo(ctrl_div);

        return group;
    },

    createHiddenInput: function(name, label, value, help_text, readonly) {
        var group = $("<div>")
            .addClass("control-group hidden")
            .addClass("control-item-" + name);

        var controller = $("<input>")
            .addClass("editor-control")
            .attr("type", "hidden")
            .val(value)
            .appendTo(group);

        if (readonly) {
            controller.attr("readonly", "readonly");
        }

        return group;
    },

    createTextInput: function(name, label, value, help_text, readonly) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "text")
            .val(value);

        if (readonly) {
            controller.attr("readonly", "readonly");
        }

        return this.createControlGroup(name, controller, label, help_text);
    },

    createNumberInput: function(name, label, value, help_text, readonly) {
        var controller = $("<input>")
            .addClass("form-control editor-control text-input-control")
            .attr("type", "number")
            .val(value);

        if (readonly) {
            controller.attr("readonly", "readonly");
        }

        return this.createControlGroup(name, controller, label, help_text);
    },

    createTextArea: function(name, label, value, help_text, readonly) {
        var controller = $("<textarea>")
            .addClass("form-control editor-control text-area-control")
            .attr("rows", "5")
            .val(value);

        if (readonly) {
            controller.attr("readonly", "readonly");
        }

        return this.createControlGroup(name, controller, label, help_text);
    },

    createSelect: function(name, label, value, help_text, options, readonly) {
        var controller = $("<select>")
            .addClass("form-control editor-control select-control")
            .val(value);

        if (readonly) {
            controller.attr("disabled", "disabled");
        }

        for (var i = 0; i < options.length; i++) {
            var option = $("<option>")
                .text(options[i][1])
                .attr("value", options[i][0])
                .appendTo(controller);

            if (options[i][0] == value) {
                option.attr("selected", "selected");
            }
        }
        
        return this.createControlGroup(name, controller, label, help_text);
    },

    createCheckBox: function(name, label, value, help_text, check, readonly) {
        var group = $("<div>")
            .addClass("control-group")
            .addClass("control-item-" + name);

        // controller
        var ctrl_div = $("<div>")
            .addClass("controls")
            .appendTo(group);

        var controller = $("<input>")
            .addClass("form-control editor-control check-box-control")
            .attr("type", "checkbox")
            .appendTo(ctrl_div);

        if (readonly) {
            controller.attr("readonly", "readonly");
        }

        if (value) {
            controller.attr("checked", "checked");
        }

        // label
        var label_div = $("<label>")
            .addClass("control-label")
            .text(label)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("help-block")
            .text(help_text)
            .appendTo(ctrl_div);

        $("<p>")
            .addClass("message-block")
            .html("&nbsp;")
            .hide()
            .appendTo(ctrl_div);
        
        return group;
    },

    createAreaSelect: function(name, label, value, help_text, areas, readonly) {
        var ctrl = $("<div>");

        // Add area.
        var select_area = $("<select>")
            .addClass("select-area form-control select-control");

        if (readonly) {
            select_area.attr("disabled", "disabled");
        }

        var selected_area = "";
        var first_area = "";
        for (var key in areas) {
            if (!first_area) {
                first_area = key;
            }
            var area = areas[key];

            var option = $("<option>")
                .text(area.name)
                .attr("value", key)
                .appendTo(select_area);

            if (!selected_area) {
                for (var r = 0; r < area.rooms.length; r++) {
                    if (area.rooms[r][0] == value) {
                        option.attr("selected", "selected");
                        selected_area = key;
                        break;
                    }
                }
            }
        }
        select_area.appendTo(ctrl);
        select_area.on("change", controller.onAreaChange);

        if (!selected_area) {
            selected_area = first_area;
        }

        // Add room.
        var select_room = $("<select>")
            .addClass("select-room form-control editor-control select-control");

        if (readonly) {
            select_room.attr("disabled", "disabled");
        }

        var room_area = areas[selected_area];
        for (var i = 0; i < room_area.rooms.length; i++) {
            var room = room_area.rooms[i];

            var option = $("<option>")
                .text(room[1])
                .attr("value", room[0])
                .appendTo(select_room);

            if (room[0] == value) {
                option.attr("selected", "selected");
            }
        }
        select_room.appendTo(ctrl);
        
        return this.createControlGroup(name, ctrl, label, help_text);
    },

    createImageInput: function(image_type, name, label, value, help_text, readonly) {
        var ctrl = $("<div>");

        var image = $("<img>")
            .addClass("editor-image image-" + image_type)
            .addClass("image-item-" + name)
            .attr("src", "../images/empty.png")
            .appendTo(ctrl);
            
        var buttons = $("<div>")
            .addClass("form-control control-buttons")
            .appendTo(ctrl);

        if (readonly) {
            buttons.attr("readonly", "readonly");
        }

        var del = $("<input>")
            .attr("type", "button")
            .attr("value", "Delete")
            .appendTo(buttons);
            
        var input = $("<input>")
            .addClass("image-input-control")
            .attr("type", "file")
            .data("image_type", image_type)
            .data("field_name", name)
            .appendTo(buttons);

        if (readonly) {
            input.attr("readonly", "readonly");
        }

        var resource = $("<input>")
            .addClass("editor-control")
            .attr("type", "hidden")
            .appendTo(buttons);
            
        del.on("click", function(e){
            var parent = $(this).parent().parent();
            parent.find("img").attr("src", "../images/empty.png");
            parent.find(".image-input-control").val("");
            parent.find(".editor-control").val("");
        });

        if (value) {
            image.attr("src", CONFIG.resource_url + value);
            resource.val(value);
        }

        return this.createControlGroup(name, ctrl, label, help_text);
    },
}
