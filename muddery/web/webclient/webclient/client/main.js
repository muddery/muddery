
window.mudcore = {
};

mudcore.client = new MudderyClient();
mudcore.service = new MudderyService();
mudcore.text2html = new MudderyText2HTML();
mudcore.text_escape = new MudderyTextEscape();
mudcore.map_data = new MudderyMapData();
mudcore.data_handler = new MudderyDataHandler();
mudcore.utils = new MudderyUtils();
mudcore.local_string = new MudderyLocalString();
mudcore.trans = function(str) {
	return mudcore.local_string.translate(str);
}

window.main_window = new MudderyMain($("#main-window"));
window.login_window = new MudderyLogin($("#login-window"));
window.select_char_window = new MudderySelectChar($("#select-char-window"));
window.new_char_window = new MudderyNewChar($("#new-char-window"));

window.main_game_window = new MudderyMainGame($("#game-window"));
window.prompt_bar = new MudderyPromptBar($("#prompt-bar"));
window.scene_window = new MudderyScene($("#scene-window"));
window.message_window = new MudderyMessage($("#message-window"));
window.char_data_window = new MudderyCharData($("#char-data-window"));
window.inventory_window = new MudderyInventory($("#inventory-window"));
window.skills_window = new MudderySkills($("#skills-window"));
window.quests_window = new MudderyQuests($("#quests-window"));

window.popup_message = new MudderyPopupMessage($("#popup-message"));
window.popup_object = new MudderyPopupObject($("#popup-object"));
window.popup_get_objects = new MudderyPopupGetObjects($("#popup-get-objects"));

$(document).ready(function() {
    main_window.init();
    login_window.init();
    select_char_window.init();
    new_char_window.init();

    main_game_window.init();
    prompt_bar.init();
    scene_window.init();
    message_window.init();
    char_data_window.init();
    inventory_window.init();
    skills_window.init();
    quests_window.init();

    popup_message.init();
    popup_object.init();
    popup_get_objects.init();

    mudcore.client.init();
});
