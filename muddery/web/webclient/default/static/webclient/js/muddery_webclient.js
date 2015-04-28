/*
Muddery webclient (javascript component)
*/

var DISPLAY_MAP = {
    "msg" : display_msg,
    "err" : display_err,
    "sys" : display_sys,
    "debug" : display_debug,
    "prompt" : display_prompt,
    "env" : display_env
};

var ENVIROMENT = {
    "room_name" : "",
    "room_desc" : "",
    "objects" : [],
    "players" : [],
    "exits" : [],
}

function display_data(data){
    for (var key in data){
        if (key in DISPLAY_MAP){
            try {
                DISPLAY_MAP[key](data[key]);
            }
            catch(error){
                display_err("Data error.");
            }
        }
        else{
            display_msg(data[key]);
        }
    }
}


function display_msg(data) {
    display_text_msg("out", data);
}


function display_err(data) {
    display_text_msg("err", data);
}


function display_sys(data) {
    display_text_msg("sys", data);
}


function display_debug(data) {
    display_text_msg("debug", data);
}


function display_prompt(data) {
    display_text_msg("prompt", data);
}


function display_text_msg(type, msg) {
    $("#msg_wnd").stop(true);
    $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
    
    $("#msg_wnd").append("<div class='msg "+ type +"'>"+ msg +"</div>");
    var max = 40;
    while ($("#msg_wnd div").size() > max) {
        $("#msg_wnd div:first").remove();
    }
    // scroll message window to bottom
    //$("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
    $("#msg_wnd").animate({scrollTop: $("#msg_wnd")[0].scrollHeight});
}


function display_env(data) {
    $("#env_wnd").empty();
    
    if ("room_name" in data){
        ENVIROMENT["room_name"] = data["room_name"];
    }
    if ("room_desc" in data){
        ENVIROMENT["room_desc"] = data["room_desc"];
    }
    if ("objects" in data){
        ENVIROMENT["objects"] = data["objects"];
    }
    if ("players" in data){
        ENVIROMENT["players"] = data["players"];
    }
    if ("exits" in data){
        ENVIROMENT["exits"] = data["exits"];
    }

    var split = "****************************************";
    var text = "<div class='msg out'>"+ split +"</div>";
    text += "<div class='msg out'>"+ ENVIROMENT["room_name"] +"</div>";
    text += "<div class='msg out'>"+ split +"</div>";
    text += "<div><br></div>";
    text += "<div class='msg out'>"+ ENVIROMENT["room_desc"] +"</div>";
    
    $("#env_wnd").append(text);
}