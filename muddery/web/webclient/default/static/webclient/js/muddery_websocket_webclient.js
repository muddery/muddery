
function doShow(type, msg) {
    if (type == "out") {
        try {
            var data = JSON.parse(msg);
        }
        catch(err) {
            // not JSON packed - a normal text message
            var data = {"out": msg};
        }
    }
    else if (type == "err") {
        var data = {"err": msg};
    }
    else if (type == "sys") {
        var data = {"sys": msg};
    }
    else if (type == "debug") {
        var data = {"debug": msg};
    }
                
    webclient.displayData(data);
}

function doPrompt(type, msg) {
    var data = {"prompt": msg};
    webclient.displayData(data);
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

