
/***************************************
 *
 * Create the main framework.
 *
 ***************************************/

MudderyMain = function() {
}

MudderyMain.prototype = {
    // Init the main frame.
    init: function() {
        var core = {};
        window.core = core;
        core.client = new MudderyClient();
        core.service = new MudderyService();
        core.text2html = new MudderyText2HTML();
        core.text_escape = new MudderyTextEscape();
        core.map_data = new MudderyMapData();
        core.data_handler = new MudderyDataHandler();
        core.utils = new MudderyUtils();
        core.local_string = new MudderyLocalString();
        core.local_string.set_dict(MudderyLocalDict);
        core.trans = function(str) {
            return core.local_string.translate(str);
        }

        var mud = {};
        window.mud = mud;

        mud.main_frame = new MudderyMainFrame($("#main-frame"));
        mud.main_frame.init();

        mud.login_window = new MudderyLogin($("#login-window"));
        mud.login_window.init();

        mud.select_char_window = new MudderySelectChar($("#select-char-window"));
        mud.select_char_window.init();

        mud.new_char_window = new MudderyNewChar($("#new-char-window"));
        mud.new_char_window.init();

        mud.password_window = new MudderyPassword($("#password-window"));
        mud.password_window.init();

        mud.main_game_window = new MudderyMainGame($("#game-window"));
        mud.main_game_window.init();

        mud.prompt_bar = new MudderyPromptBar($("#main-contents .prompt-bar"));
        mud.prompt_bar.init();

        mud.scene_window = new MudderyScene($("#main-contents .scene-window"));
        mud.scene_window.init();

        mud.message_window = new MudderyMessage($("#main-contents .message-window"));
        mud.message_window.init();

        mud.char_data_window = new MudderyCharData($("#char-data-window"));
        mud.char_data_window.init();

        mud.inventory_window = new MudderyInventory($("#inventory-window"));
        mud.inventory_window.init();

        mud.skills_window = new MudderySkills($("#skills-window"));
        mud.skills_window.init();

        mud.quests_window = new MudderyQuests($("#quests-window"));
        mud.quests_window.init();

        mud.map_window = new MudderyMap($("#map-window"));
        mud.map_window.init();

        mud.shop_window = new MudderyShop($("#shop-window"));
        mud.shop_window.init();

        mud.goods_window = new MudderyGoods($("#goods-window"));
        mud.goods_window.init();

        mud.combat_window = new MudderyCombat($("#combat-window .combat-scene"));
        mud.combat_window.init();

        mud.combat_result_window = new MudderyCombatResult($("#combat-window .combat-result"));
        mud.combat_result_window.init();

        mud.popup_message = new MudderyPopupMessage($("#popup-message"));
        mud.popup_message.init();

        mud.popup_object = new MudderyPopupObject($("#popup-object"));
        mud.popup_object.init();

        mud.popup_get_objects = new MudderyPopupGetObjects($("#popup-get-objects"));
        mud.popup_get_objects.init();

        mud.popup_dialogue = new MudderyPopupDialogue($("#popup-dialogue"));
        mud.popup_dialogue.init();

        // Connect to the server.
        core.client.init();
    }
}

$(document).ready(function() {
    // Init the client, connect to the server.
    var main = new MudderyMain();
    main.init();
});
