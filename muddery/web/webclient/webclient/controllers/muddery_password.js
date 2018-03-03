//@ sourceURL=/controller/muddery_password.js

/*
 * Derive from the base class.
 */
function MudderyPassword() {
	BaseController.call(this);
}

MudderyPassword.prototype = prototype(BaseController.prototype);
MudderyPassword.prototype.constructor = MudderyPassword;

/*
 * Reset the view's language.
 */
MudderyPassword.prototype.resetLanguage = function() {
    $("#view_current").text($$("Current Password"));
    $("#current_password").attr("placeholder", $$("current password"));
    $("#view_password").text($$("New Password"));
    $("#new_password").attr("placeholder", $$("new password"));
    $("#password_verify").attr("placeholder", $$("password verify"));
    $("#button_change").text($$("Change"));
}

/*
 * Bind events.
 */
MudderyPassword.prototype.bindEvents = function() {
	this.onClick("#button_change", this.onChange);
}

/*
 * Event when clicks the register button.
 */
MudderyPassword.prototype.onChange = function(element) {
    var current = $("#current_password").val();
    var password = $("#new_password").val();
    var password_verify = $("#password_verify").val();

    $$.commands.doChangePassword(current, password, password_verify);
    this.clearValues();
}

/*
 * Clear user inputted values.
 */
MudderyPassword.prototype.clearValues = function() {
    $("#current_password").val("");
    $("#new_password").val("");
    $("#password_verify").val("");
}
