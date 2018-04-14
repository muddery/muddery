
if (typeof(require) != "undefined") {
    require("../controllers/base_controller.js");
}

/*
 * Derive from the base class.
 */
MudderyPassword = function(el) {
	BaseTabController.call(this, el);
}

MudderyPassword.prototype = prototype(BaseTabController.prototype);
MudderyPassword.prototype.constructor = MudderyPassword;

/*
 * Reset the view's language.
 */
MudderyPassword.prototype.resetLanguage = function() {
    this.select("#password_view_current").text($$.trans("Current Password"));
    this.select("#current_password").attr("placeholder", $$.trans("current password"));
    this.select("#password_view_password").text($$.trans("New Password"));
    this.select("#new_password").attr("placeholder", $$.trans("new password"));
    this.select("#password_verify").attr("placeholder", $$.trans("password verify"));
    this.select("#password_button_change").text($$.trans("Change"));
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
