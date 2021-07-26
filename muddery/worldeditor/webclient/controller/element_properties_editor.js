
/*
 * Derive from the base class.
 */
ElementPropertiesEditor = function() {
	CommonEditor.call(this);

    this.table_name = "element_properties";
    this.element_type = "";
    this.element_key = "";
    this.level = "";
}

ElementPropertiesEditor.prototype = prototype(CommonEditor.prototype);
ElementPropertiesEditor.prototype.constructor = ElementPropertiesEditor;


ElementPropertiesEditor.prototype.init = function() {
    this.element_type = utils.getQueryString("element_type");
    this.element_key = utils.getQueryString("element_key");
    var level = utils.getQueryString("level");
    if (level) {
        this.level = parseInt(level);
    }
    else if (level === "") {
        this.level = "";
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

ElementPropertiesEditor.prototype.refresh = function() {
    var level = this.level === null? "": this.level;
    service.queryElementLevelProperties(this.element_type, this.element_key, level, this.queryFormSuccess, this.failedCallback);
}

// Add form fields to the web page.
ElementPropertiesEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        if (field.name == "key") {
            field.value = this.element_key;
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

ElementPropertiesEditor.prototype.saveForm = function(callback_success, callback_failed, context) {
    var level = "";
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
                        if (value) {
                            level = parseInt(value);
                        }
                    }
                }
            }
        }
    }

    service.saveElementLevelProperties(
        this.element_type,
        this.element_key,
        level,
        values,
        callback_success,
        callback_failed,
        context
    );
}