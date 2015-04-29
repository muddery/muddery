
function doShow(type, msg){
    if (type == "out"){
        try {
            var data = JSON.parse(msg);
        }
        catch(err){
            // not JSON packed - a normal text message
            var data = {"out": msg};
        }
    }
    else if (type == "err"){
        var data = {"err": msg};
    }
    else if (type == "sys"){
        var data = {"sys": msg};
    }
    else if (type == "debug"){
        var data = {"debug": msg};
    }
                
    display_data(data);
}

function doPrompt(type, msg){
    var data = {"prompt": msg};
    display_data(data);
}
