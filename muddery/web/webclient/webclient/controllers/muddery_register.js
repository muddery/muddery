//@ sourceURL=/controller/muddery_register.js

/*
 * Derive from the base class.
 */
function MudderyRegister() {
	BaseController.call(this);
}

MudderyRegister.prototype = prototype(BaseController.prototype);
MudderyRegister.prototype.constructor = MudderyRegister;

/*
 * Reset the view's language.
 */
MudderyRegister.prototype.resetLanguage = function() {
    $("#view_name").text($$("Name"));
    $("#reg_name").attr("placeholder", $$("username"));
    $("#view_password").text($$("Password"));
    $("#reg_password").attr("placeholder", $$("password"));
    $("#reg_password_verify").attr("placeholder", $$("password verify"));
    $("#button_register").text($$("Register"));
}

/*
 * Bind events.
 */
MudderyRegister.prototype.bindEvents = function() {
	this.onClick("#button_register", this.onRegister);
}

/*
 * Event when clicks the register button.
 */
MudderyRegister.prototype.onRegister = function(element) {
    var playername = $("#reg_name").val();
    var password = $("#reg_password").val();
    var password_verify = $("#reg_password_verify").val();

    $$.commands.doRegister(playername, password, password_verify, true);
    this.clearValues();
}

/*
 * Clear user inputted values.
 */
MudderyRegister.prototype.clearValues = function() {
    $("#reg_name").val("");
    $("#reg_password").val("");
    $("#reg_password_verify").val("");
}
