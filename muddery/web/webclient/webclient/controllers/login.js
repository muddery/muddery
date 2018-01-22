//@ sourceURL=/controller/login.js

/*
 * Derive from the base class.
 */
function MudderyLogin(root_controller) {
	BaseController.call(this, root_controller);
}

MudderyLogin.prototype = prototype(BaseController.prototype);
MudderyLogin.prototype.constructor = MudderyLogin;

/*
 * Reset the view's language.
 */
MudderyLogin.prototype.resetLanguage = function() {
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
MudderyLogin.prototype.bindEvents = function() {
    this.onClick("#check_save_password", this.onSavePassword);
    this.onClick("#button_login", this.onLogin);
}

/*
 * Event on click the login button.
 */
MudderyLogin.prototype.onLogin = function(element) {
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
MudderyLogin.prototype.onSavePassword = function(element) {
    var save_password = $("#cb_save_password").is(":checked");
    $$.commands.doSavePassword(save_password);

    if (!save_password) {
        $("#cb_auto_login").removeAttr("checked");
    }
}
    
/*
 * Set player's name.
 */
MudderyLogin.prototype.setPlayerName = function(playername) {
    $("#login_name").val(playername);
    $("#login_password").val("");
}
