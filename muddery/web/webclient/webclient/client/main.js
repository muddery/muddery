
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
window.message_window = new MudderyMessage($("#message-window"));

$(document).ready(function() {
    main_window.init();
    login_window.init();
    select_char_window.init();
    message_window.init();

    mudcore.client.init();
});
