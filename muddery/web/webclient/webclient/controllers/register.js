//@ sourceURL=/controller/register.js

/*
 * Derive from the base class.
 */
function Controller(root_controller) {
	BaseController.call(this, root_controller);
}

Controller.prototype = prototype(BaseController.prototype);
Controller.prototype.constructor = Controller;

/*
 * Reset the view's language.
 */
Controller.prototype.resetLanguage = function() {
    $("#view_name").text($$("Name"));
    $("#reg_name").attr("placeholder", $$("username"));
    $("#view_password").text($$("Password"));
    $("#reg_password").attr("placeholder", $$("password"));
    $("#reg_password_verify").attr("placeholder", $$("password verify"));
    $("#button_register").text($$("Register"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#button_register").bind("click", this.onRegister);
}

/*
 * Event when clicks the register button.
 */
Controller.prototype.onRegister = function(event) {
    var playername = $("#reg_name").val();
    var password = $("#reg_password").val();
    var password_verify = $("#reg_password_verify").val();

    $$.commands.doRegister(playername, password, password_verify, true);
    controller.clearValues();
}

/*
 * Clear user inputted values.
 */
Controller.prototype.clearValues = function() {
    $("#reg_name").val("");
    $("#reg_password").val("");
    $("#reg_password_verify").val("");
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});
