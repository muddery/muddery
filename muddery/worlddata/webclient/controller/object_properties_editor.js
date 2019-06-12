
/*
 * Derive from the base class.
 */
ObjectPropertiesEditor = function() {
	CommonEditor.call(this);

    this.table_name = "object_properties";
    this.obj_key = "";
    this.level = 0;
}

ObjectPropertiesEditor.prototype = prototype(CommonEditor.prototype);
ObjectPropertiesEditor.prototype.constructor = ObjectPropertiesEditor;


ObjectPropertiesEditor.prototype.init = function() {
    this.obj_key = utils.getQueryString("obj_key");
    this.level = utils.getQueryString("level");
    if (this.level) {
        this.level = parseInt(this.level);
    }
    else {
        this.level = null;
    }

    if (sessionStorage.page_param) {
        this.field_values = JSON.parse(sessionStorage.page_param);
    }
    else {
        this.field_values = {};
    }

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.level === null) {
        $("#delete-record").removeClass("hidden");
    }

    this.bindEvents();
    this.refresh();
}

ObjectPropertiesEditor.prototype.refresh = function() {
    var level = this.level || 0;
    service.queryObjectLevelProperties(this.obj_key, level, this.queryFormSuccess, this.failedCallback);
}

// Add form fields to the web page.
ObjectPropertiesEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        if (field.name == "key") {
            field.value = this.obj_key;
            var controller = this.createFieldController(field, true);
        }
        else {
            var controller = this.createFieldController(field);
        }

        if (controller) {
            controller.appendTo(container);
        }
    }

    window.parent.controller.setFrameSize();
}

ObjectPropertiesEditor.prototype.saveForm = function(callback_success, callback_failed, context) {
    var level = 0;
    var values = {};
    var fields = $("#fields .field-controller");
    for (var f = 0; f < fields.length; f++) {
        var name = $(fields[f]).data("field-name");
        var control = $(fields[f]).find(".editor-control");
        if (control.length > 0) {
            if (control.attr("type") == "checkbox") {
                values[name] = control.prop("checked");
            }
            else {
                // Leave the value blank if it is an empty string.
                var value = control.val();
                if (value.length > 0) {
                    values[name] = value;

                    if (name == "level") {
                        level = parseInt(value);
                    }
                }
            }
        }
    }

    service.saveObjectLevelProperties(this.obj_key,
                                      level,
                                      values,
                                      callback_success,
                                      callback_failed,
                                      context);
}