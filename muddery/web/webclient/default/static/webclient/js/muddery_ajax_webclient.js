
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

function webclient_init(){
    // Start the connection by making sure the server is ready

    $.ajax({
        type: "POST",
        url: "/webclientdata",
        async: true,
        cache: false,
        timeout: 50000,
        dataType:"json",
        data: {mode:'init', 'suid':CLIENT_HASH},

        // callback methods

        success: function(data){  // called when request to initdata completes
            $("#connecting").remove() // remove the "connecting ..." message.
            CLIENT_HASH = data.suid // unique id hash given from server

            // A small timeout to stop 'loading' indicator in Chrome
            setTimeout(function () {
                $("#playercount").fadeOut('slow', webclient_set_sizes);
            }, 10000);

            // Report success
            msg_display('sys',"Connected to " + data.msg + ". Websockets not available: Using ajax client without OOB support.");

            // Wait for input
            webclient_receive();
            webclient.onConnectionOpen();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            msg_display("err", "Connection error ..." + " (" + errorThrown + ")");
            setTimeout('webclient_receive()', 15000); // try again after 15 seconds
        },
    });
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
            webclient.onConnectionClose();
            webclient.showAlert(LS("The client connection was closed cleanly."), "OK");
        },
        error: function(XMLHttpRequest, textStatus, errorThrown){
            CLIENT_HASH = '0';
        }

    });
}

function doConnect() {
    webclient_init();
}

// Callback function - called when page is closed or moved away from.
$(window).bind("beforeunload", webclient_close);