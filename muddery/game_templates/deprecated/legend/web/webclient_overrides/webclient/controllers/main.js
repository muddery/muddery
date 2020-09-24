//@ sourceURL=/controller/main.js

/*
 * Derive from the base class.
 */
function Main() {
	MudderyMain.call(this);
}

Main.prototype = prototype(MudderyMain.prototype);
Main.prototype.constructor = Main;

/*
 * Event when the connection opens.
 */
Main.prototype.onConnectionOpen = function() {
	this.puppet = false;
	
	controller.showUnlogin();
}

/*
 * Event when the player logins.
 */
Main.prototype.onLogin = function(data) {
}
    
/*
 * Show the layout when players has not connected.
 */
Main.prototype.showConnect = function() {
	this.hideTabs();
	
	$("#tab_connect").show();
	
	controller.showContent("connect");
	
	this.leftCombatQueue();

	this.clearChannels();
}
    
/*
 * Show the layout when players puppet.
 */
Main.prototype.showPuppet = function() {
	// show login UI
	this.clearMsgWindow();

	this.clearPromptBar();
	$("#prompt_content").show();

	// show login tabs
	this.hideTabs();

	$("#tab_scene").show();
	$("#tab_status").show();
	$("#tab_inventory").show();
	$("#tab_honours").show();
	$("#tab_system").show();

	if (!this._solo_mode) {
		$("#tab_social").show();
	}

	this.showContent("scene");
}
    
/*
 * Show the layout when players unlogin.
 */
MudderyMain.prototype.showUnlogin = function() {
	// show unlogin UI
	this.clearMsgWindow();
	$("#prompt_content").hide();

	this.leftCombatQueue();

	// show unlogin tabs
	this.hideTabs();

	$("#tab_quick_login").show();

	this.showContent("quick_login");

	this.clearChannels();
}
    
/*
 * Reset the view's language.
 */
MudderyMain.prototype.resetLanguage = function() {
	$("#view_level").text($$("LEVEL: "));
	$("#view_exp").text($$("EXP: "));
	$("#view_hp").text($$("HP: "));
	$("#view_connect").text($$("Connect"));
	$("#view_quick_login").text($$("Login"));
	$("#view_scene").text($$("Scene"));
	$("#view_char").text($$("Char"));
	$("#view_status").text($$("Status"));
	$("#view_inventory").text($$("Inventory"));
	$("#view_skills").text($$("Skills"));
	$("#view_quests").text($$("Quests"));
	$("#view_honours").text($$("Honours"));
	$("#view_social").text($$("Social"));
	$("#view_map").text($$("Map"));
	$("#view_system").text($$("Sys"));
	$("#view_system_char").text($$("System"));
	$("#view_logout").text($$("Logout"));
	$("#view_logout_puppet").text($$("Logout"));
	$("#msg_send").text($$("Send"));
}
