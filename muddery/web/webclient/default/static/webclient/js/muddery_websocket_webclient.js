
var CLIENT_CONNECTED = false

function doShow(type, msg) {
    webclient.doShow(type, msg);
}

function doPrompt(type, msg) {
    doShow("prompt", msg);
}

function sendCommand(command) {
    sendRequest('CMD ' + command);
}

function sendRequest(request) {
    // relays data from client to Evennia.
    websocket.send(request);
}

function doSetSizes() {
    webclient.doSetSizes();
}

function onOpen(evt) {
    // called when client is first connecting
    $("#connecting").remove(); // remove the "connecting ..." message
    doShow("sys", "Using websockets - connected to " + wsurl + ".")

    setTimeout(function () {
        $("#numplayers").fadeOut('slow', doSetSizes);
    }, 10000);
    
    CLIENT_CONNECTED = true;
    webclient.onConnectionOpen();
}

function onClose(evt) {
    // called when client is closing
    CLIENT_HASH = 0;
    CLIENT_CONNECTED = false;
    webclient.onConnectionClose();
    popupmgr.showAlert(LS("The client connection was closed cleanly."), "OK");
}

function doConnect() {
    webclient_init();

    // set an idle timer to avoid proxy servers to time out on us (every 3 minutes)
    setInterval(function() {
        doSend("idle")
    }, 60000*3);
}
