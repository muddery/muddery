//@ sourceURL=/controller/quick_login.js

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
	$("#view_header").text($$("Please input your name."));
	$("#login_name").attr("placeholder", $$("name"));
	$("#button_login").text($$("Login"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#button_login").bind("click", this.onLogin);
}

/*
 * Event when clicks the login button.
 */
Controller.prototype.onLogin = function(event) {
    var playername = $("#login_name").val();
    $$.commands.doQuickLogin(playername);
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});