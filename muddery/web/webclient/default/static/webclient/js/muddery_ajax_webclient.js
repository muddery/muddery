
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
    
    display_data(data);
}

