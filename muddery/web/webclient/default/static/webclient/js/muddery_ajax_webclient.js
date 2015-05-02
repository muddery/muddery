
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
