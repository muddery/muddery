//@ sourceURL=/controller/muddery_login.js

/*
 * Derive from the base class.
 */
function MudderyLogin() {
	BaseController.call(this);
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
    this.on("#cb_save_password", "change", this.onSavePassword);
    this.on("#cb_auto_login", "change", this.onAutoLogin);
    this.onClick("#button_login", this.onLogin);
}

/*
 * Event on click the login button.
 */
MudderyLogin.prototype.onLogin = function(element) {
    var playername = $("#login_name").val();
    var password = $("#login_password").val();
    var save_password = $("#cb_save_password").prop("checked");
    var auto_login = $("#cb_auto_login").prop("checked");

    $("#login_password").val("");

    $$.commands.doLogin(playername, password);
    $$.commands.doSavePassword(save_password);
    $$.commands.doAutoLoginConfig(playername, password, save_password, auto_login);
}

/*
 * Event on click the save password checkbox.
 */
MudderyLogin.prototype.onSavePassword = function(element) {
    var save_password = $("#cb_save_password").prop("checked");
    $$.commands.doSavePassword(save_password);

    if (!save_password) {
        $("#cb_auto_login").prop("checked", false);
        $$.commands.doRemoveAutoLogin();
    }
}

/*
 * Event on click the auto login checkbox.
 */
MudderyLogin.prototype.onAutoLogin = function(element) {
    var auto_login = $("#cb_auto_login").prop("checked");

    if (!auto_login) {
        $$.commands.doRemoveAutoLogin();
    }
}

/*
 * Set values.
 */
MudderyLogin.prototype.setValues = function(playername, password, save_password, auto_login) {
    $("#login_name").val(playername);
    $("#login_password").val("");

    $("#login_name").val(playername);
    $("#login_password").val(password);
    $("#cb_save_password").prop("checked", save_password);
    $("#cb_auto_login").prop("checked", auto_login);
}

/*
 * Set player's name.
 */
MudderyLogin.prototype.setPlayerName = function(playername) {
    $("#login_name").val(playername);
    $("#login_password").val("");
}
