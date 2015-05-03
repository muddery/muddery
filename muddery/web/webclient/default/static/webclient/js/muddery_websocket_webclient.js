
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

function onClose(evt) {
    // called when client is closing
    CLIENT_HASH = 0;
    webclient.showAlert("Mud client connection was closed cleanly.", "OK");
}