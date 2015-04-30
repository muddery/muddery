
function msg_display(type, msg){
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
    
    webclient.displayData(data);
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
