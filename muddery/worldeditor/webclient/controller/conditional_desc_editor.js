
/*
 * Derive from the base class.
 */
ConditionalDescEditor = function() {
	CommonEditor.call(this);

    this.table_name = "conditional_desc";
    this.element_type = "";
    this.element_key = "";
}

ConditionalDescEditor.prototype = prototype(CommonEditor.prototype);
ConditionalDescEditor.prototype.constructor = ConditionalDescEditor;


ConditionalDescEditor.prototype.init = function() {
    this.element_type = utils.getQueryString("element_type");
    this.element_key = utils.getQueryString("element_key");
    this.record_id = utils.getQueryString("record");

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

// Add form fields to the web page.
ConditionalDescEditor.prototype.setFields = function() {
    var container = $("#fields");
    container.children().remove();

    for (var i = 0; i < this.fields.length; i++) {
        var field = this.fields[i];

        if (field.name == "element") {
            field.value = this.element_type;
            var controller = this.createFieldController(field, true);
        }
        else if (field.name == "key") {
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
