//@ sourceURL=/controller/login.js

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
    $("#view_header").text($$("Please login."));
    $("#login_name").attr("placeholder", $$("username"));
    $("#login_password").attr("placeholder", $$("password"));
    $("#check_save_password").text($$("Save Password"));
    $("#check_auto_login").text($$("Auto Login"));
    $("#button_login").text($$("Login"));
}

/*
 * Bind events.
 */
Controller.prototype.bindEvents = function() {
    $("#check_save_password").bind("click", this.onSavePassword);
	$("#button_login").bind("click", this.onLogin);
}

/*
 * Event on click the login button.
 */
Controller.prototype.onLogin = function() {
    var playername = $("#login_name").val();
    var password = $("#login_password").val();
    var save_password = $("#cb_save_password").is(":checked");
    var auto_login = $("#cb_auto_login").is(":checked");

    $("#login_password").val("");

    $$.commands.doLogin(playername, password);
    $$.commands.doAutoLoginConfig(playername, password, save_password, auto_login);
}

/*
 * Event on click the save password checkbox.
 */
Controller.prototype.onSavePassword = function() {
    var save_password = $("#cb_save_password").is(":checked");
    $$.commands.doSavePassword(save_password);

    if (!save_password) {
        $("#cb_auto_login").removeAttr("checked");
    }
}
    
/*
 * Set player's name.
 */
Controller.prototype.setPlayerName = function(playername) {
    $("#login_name").val(playername);
    $("#login_password").val("");
}

var controller = new Controller(parent);

$(document).ready(function() {
	controller.onReady();
});