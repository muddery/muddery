
if (typeof(require) != "undefined") {
    require("./base_controller.js");
}

/*
 * Derive from the base class.
 */
function MudderyQuickLogin(el) {
	BaseController.call(this, el);
}

MudderyQuickLogin.prototype = prototype(BaseController.prototype);
MudderyQuickLogin.prototype.constructor = MudderyQuickLogin;

/*
 * Reset the view's language.
 */
MudderyQuickLogin.prototype.resetLanguage = function() {
	this.select("#quick_login_view_header").text($$.trans("Please input your name."));
	this.select("#quick_login_name").attr("placeholder", $$.trans("name"));
	this.select("#button_quick_login").text($$.trans("Login"));
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
    var playername = this.select("#login_name").val();
    $$.commands.doQuickLogin(playername);
}
