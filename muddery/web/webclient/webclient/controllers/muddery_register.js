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
    this.select("#register_view_name").text($$("Name"));
    this.select("#reg_name").attr("placeholder", $$("username"));
    this.select("#register_view_password").text($$("Password"));
    this.select("#reg_password").attr("placeholder", $$("password"));
    this.select("#reg_password_verify").attr("placeholder", $$("password verify"));
    this.select("#button_register").text($$("Register"));
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
    var playername = this.select("#reg_name").val();
    var password = this.select("#reg_password").val();
    var password_verify = this.select("#reg_password_verify").val();

    $$.commands.doRegister(playername, password, password_verify, true);
    this.clearValues();
}

/*
 * Clear user inputted values.
 */
MudderyRegister.prototype.clearValues = function() {
    this.select("#reg_name").val("");
    this.select("#reg_password").val("");
    this.select("#reg_password_verify").val("");
}
