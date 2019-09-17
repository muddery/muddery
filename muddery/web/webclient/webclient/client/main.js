
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
window.message_window = new MudderyMessage($("#message-window"));
window.char_data_window = new MudderyCharData($("#char-data-window"));

window.popup_message = new MudderyPopupMessage($("#popup-message"));

$(document).ready(function() {
    main_window.init();
    login_window.init();
    select_char_window.init();
    new_char_window.init();
    message_window.init();

    mudcore.client.init();
});
