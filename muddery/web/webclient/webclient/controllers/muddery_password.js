
/*
 * Derive from the base class.
 */
function MudderyPassword(el) {
	BaseController.call(this, el);
}

MudderyPassword.prototype = prototype(BaseController.prototype);
MudderyPassword.prototype.constructor = MudderyPassword;

/*
 * Reset the view's language.
 */
MudderyPassword.prototype.resetLanguage = function() {
    this.select("#password_view_current").text($$("Current Password"));
    this.select("#current_password").attr("placeholder", $$("current password"));
    this.select("#password_view_password").text($$("New Password"));
    this.select("#new_password").attr("placeholder", $$("new password"));
    this.select("#password_verify").attr("placeholder", $$("password verify"));
    this.select("#password_button_change").text($$("Change"));
}

/*
 * Bind events.
 */
MudderyPassword.prototype.bindEvents = function() {
	this.onClick("#password_button_change", this.onChange);
}

/*
 * Event when clicks the register button.
 */
MudderyPassword.prototype.onChange = function(element) {
    var current = this.select("#current_password").val();
    var password = this.select("#new_password").val();
    var password_verify = this.select("#password_verify").val();

    $$.commands.doChangePassword(current, password, password_verify);
    this.clearValues();
}

/*
 * Clear user inputted values.
 */
MudderyPassword.prototype.clearValues = function() {
    this.select("#current_password").val("");
    this.select("#new_password").val("");
    this.select("#password_verify").val("");
}
