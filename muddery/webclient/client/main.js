
/***************************************
 *
 * Create the main framework.
 *
 ***************************************/

MudderyMain = function() {
}

MudderyMain.prototype.init = function() {
    // Init the main frame.
    this.loadCore();
    this.loadFrame();
    this.initFrame();
}

MudderyMain.prototype.loadCore = function() {
    var core = {};
    window.core = core;

    core.client = new MudderyClient();
    core.service = new MudderyService();
    core.command = new MudderyCommand();
    core.text2html = new MudderyText2HTML();
    core.text_escape = new MudderyTextEscape();
    core.map_data = new MudderyMapData();
    core.data_handler = new MudderyDataHandler();
    core.utils = new MudderyUtils();
    core.crypto = new MudderyCrypto();
    core.local_string = new MudderyLocalString();
    core.local_string.set_dict(MudderyLocalDict);
    core.trans = function(str) {
        return core.local_string.translate(str);
    }
}

MudderyMain.prototype.loadFrame = function() {
    var mud = {};
    window.mud = mud;

    mud.main_frame = new MudderyMainFrame($("#main-frame"));
    mud.login_window = new MudderyLogin($("#login-window"));
    mud.select_char_window = new MudderySelectChar($("#select-char-window"));
    mud.new_char_window = new MudderyNewChar($("#new-char-window"));
    mud.password_window = new MudderyPassword($("#password-window"));
    mud.game_window = new MudderyGame($("#game-window"));
    mud.scene_window = new MudderyScene($("#scene-window"));
    mud.char_data_window = new MudderyCharData($("#char-data-window"));
    mud.inventory_window = new MudderyInventory($("#inventory-window"));
    mud.skills_window = new MudderySkills($("#skills-window"));
    mud.quests_window = new MudderyQuests($("#quests-window"));
    mud.honour_window = new MudderyHonour($("#honour-window"));
    mud.map_window = new MudderyMap($("#map-window"));
    mud.shop_window = new MudderyShop($("#shop-window"));
    mud.combat_window = new MudderyCombat($("#combat-window"));
    mud.conversation_window = new MudderyConversation($("#conversation-window"));
    mud.popup_alert = new MudderyPopupMessage($("#popup-alert"));
    mud.popup_message = new MudderyPopupMessage($("#popup-message"));
    mud.popup_object = new MudderyPopupObject($("#popup-object"));
    mud.popup_get_objects = new MudderyPopupGetObjects($("#popup-get-objects"));
    mud.popup_dialogue = new MudderyPopupDialogue($("#popup-dialogue"));
    mud.popup_confirm_combat = new MudderyPopupConfirmCombat($("#popup-confirm-combat"));
    mud.popup_input_command = new MudderyPopupInputCommand($("#popup-input-command"));
}

MudderyMain.prototype.initFrame = function() {
    for (var key in window.mud) {
        window.mud[key].init();
    }

    // Connect to the server.
    core.client.init();
}
