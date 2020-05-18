
/*
 * Derive from the base class.
 */
SettingsEditor = function() {
	CommonEditor.call(this);
}

SettingsEditor.prototype = prototype(CommonEditor.prototype);
SettingsEditor.prototype.constructor = SettingsEditor;

SettingsEditor.prototype.init = function() {
    this.table_name = utils.getQueryString("table");

    $("#exit-button").removeClass("hidden");
    $("#save-record").removeClass("hidden");

    $("#form-name").text(this.table_name);

    this.bindEvents();
    this.refresh();
}

SettingsEditor.prototype.refresh = function() {
    service.queryFormFirstRecord(this.table_name, this.queryFormSuccess, this.queryFormFailed);
}

SettingsEditor.prototype.queryFormSuccess = function(data) {
    // get record id
    for (var i = 0; i < data.length; i++) {
        if (data[i].name == "id") {
            controller.record_id = data[i].value;
            break;
        }
    }

    CommonEditor.prototype.queryFormSuccess.call(this, data);
}