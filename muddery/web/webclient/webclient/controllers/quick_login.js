//@ sourceURL=/controller/quick_login.js

/*
 * Derive from the base class.
 */
function MudderyQuickLogin(root_controller) {
	BaseController.call(this, root_controller);
}

MudderyQuickLogin.prototype = prototype(BaseController.prototype);
MudderyQuickLogin.prototype.constructor = MudderyQuickLogin;

/*
 * Reset the view's language.
 */
MudderyQuickLogin.prototype.resetLanguage = function() {
	$("#view_header").text($$("Please input your name."));
	$("#login_name").attr("placeholder", $$("name"));
	$("#button_login").text($$("Login"));
}

/*
 * Bind events.
 */
MudderyQuickLogin.prototype.bindEvents = function() {
    this.onClick("#button_login", this.onLogin);
}

/*
 * Event when clicks the login button.
 */
MudderyQuickLogin.prototype.onLogin = function(element) {
    var playername = $("#login_name").val();
    $$.commands.doQuickLogin(playername);
}
