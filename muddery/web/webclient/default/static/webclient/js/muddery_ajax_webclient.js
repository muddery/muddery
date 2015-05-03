
function msg_display(type, msg){
    webclient.doShow(type, msg);
}

function sendCommand(command) {
    sendRequest(command);
}

function sendRequest(request) {
    // relays data from client to Evennia.
    webclient_input(request);
}

function webclient_set_sizes() {
    webclient.doSetSizes();
}

function webclient_close(){
    // Kill the connection and do house cleaning on the server.
    $.ajax({
        type: "POST",
        url: "/webclientdata",
        async: false,
        cache: false,
        timeout: 50000,
        dataType: "json",
        data: {mode: 'close', 'suid': CLIENT_HASH},

        success: function(data){
            CLIENT_HASH = '0';
            webclient.showAlert("Mud client connection was closed cleanly.", "OK");
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            CLIENT_HASH = '0';
        }

    });
}

// Callback function - called when page is closed or moved away from.
$(window).bind("beforeunload", webclient_close);