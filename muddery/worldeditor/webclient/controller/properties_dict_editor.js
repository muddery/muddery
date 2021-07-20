
/*
 * Derive from the base class.
 */
PropertiesDictEditor = function() {
	CommonEditor.call(this);

    this.table_name = "properties_dict";
    this.record_id = "";
    this.element_type = "";
}

PropertiesDictEditor.prototype = prototype(CommonEditor.prototype);
PropertiesDictEditor.prototype.constructor = PropertiesDictEditor;


PropertiesDictEditor.prototype.init = function() {
    this.element_type = utils.getQueryString("element_type");
    this.record_id = utils.getQueryString("record");
    if (sessionStorage.page_param) {
        this.field_values = JSON.parse(sessionStorage.page_param);
    }
    else {
        this.field_values = {};
    }

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");
    if (this.record_id) {
        $("#delete-record").removeClass("hidden");
    }

    this.bindEvents();
    this.refresh();
}

// Add form fields to the web page.
PropertiesDictEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        if (field.name == "element_type") {
            field.value = this.element_type;
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