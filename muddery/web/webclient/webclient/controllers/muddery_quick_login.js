//@ sourceURL=/controller/muddery_quick_login.js

/*
 * Derive from the base class.
 */
function MudderyQuickLogin() {
	BaseController.call(this);
}

MudderyQuickLogin.prototype = prototype(BaseController.prototype);
MudderyQuickLogin.prototype.constructor = MudderyQuickLogin;

/*
 * Reset the view's language.
 */
MudderyQuickLogin.prototype.resetLanguage = function() {
	this.select("#quick_login_view_header").text($$("Please input your name."));
	this.select("#quick_login_name").attr("placeholder", $$("name"));
	this.select("#button_quick_login").text($$("Login"));
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
