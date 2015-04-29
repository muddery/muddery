/*
Muddery webclient (javascript component)
*/

var DISPLAY_MAP = {
    "msg" : display_msg,
    "out" : display_out,
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
    data = text2html.parse_html(data);
    display_text_msg("msg", data);
}


function display_out(data) {
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


function doSetSizes() {
    // Sets the size of the message window
    var win_h = $(window).innerHeight();
    var win_w = $(window).innerWidth();
    var close_h = $('#close_button').outerHeight(true);
    var prom_h = $('#input_prompt').outerHeight(true);
    var add_h = $('#input_additional').outerHeight(true);
    $('#input_box').height(close_h + prom_h + add_h);
    
    var inp_h = $('#input_box').outerHeight(true);
    var inp_w = $('#input_box').outerWidth(true);
    //$("#wrapper").css({'height': win_h - inp_h - 1});
    $('#input_box').css({'left': (win_w - inp_w) / 2, 'top': (win_h - inp_h) / 2});

    if (win_h > 480) {
   	 	var head_h = $('#site-title').outerHeight(true);
   	 	$('#header_bar').show();
    	$('#wrapper').height(win_h - head_h - 6);
    }
    else {
    	$('#header_bar').hide();
    	$('#wrapper').height(win_h - 6);
    }
    
    var middle_h = $('#middlewindow').outerHeight(true);
    var bottom_h = $('#bottomwindow').outerHeight(true);
    $('#msg_wnd').height(middle_h - bottom_h - 2);
    
    if (win_w > 960) {
      	$('#middlewindow').width(960);
      	$('#bottomwindow').width(960);
    }
    else {
    	$('#middlewindow').width(win_w);
      	$('#bottomwindow').width(win_w);
    }
}

function doCancel() {
	websocket.send(CMD_NOINPUT);
	doCloseInput();
}

function doRequest() {
    var val = $("#input_text").val();
    $("#inputfield").val(val);
    $("#input_text").val("");
    doSend();
    doCloseInput();
}

function doInputText(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	var input = '<div><input type="' + type + '" id="input_text" value="" autocomplete="off"/></div>';
	var button = '<div>\
                    <input type="button" id="button_left" value="CANCEL" class="btn" onClick="doCancel()"/>\
                    <input type="button" id="button_right" value="  OK  " class="btn btn-primary" onClick="doRequest()"/>\
              	  </div>'
	$('#input_additional').html(input + button);
    $('#input_text').focus();
    doSetSizes();
}

function doInputCmd(type, msg) {
    createInputCmdDlg();
	$('#input_prompt').html(msg);
	var input = '<div><input type="' + type + '" id="input_text" value="" autocomplete="off"/></div>';
	var button = '<div>\
                    <input type="button" id="button_left" value="CANCEL" class="btn" onClick="doCloseInput()"/>\
                    <input type="button" id="button_right" value="  OK  " class="btn btn-primary" onClick="doRequest()"/>\
              	  </div>'
	$('#input_additional').html(input + button);
    $('#input_text').focus();
    doSetSizes();
}

function doInputLink(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	$('#input_additional').html('<p/>');
	doSetSizes();
}

function doAlert(type, msg) {
    createInputTextDlg();
	$('#input_prompt').html(msg);
	var button = '<div><br></div>\
                  <div>\
                    <center>\
                      <input type="button" id="button_center" value="  OK  " class="btn btn-primary" onClick="doCloseInput()"/>\
                    </center>\
              	  </div>'
	$('#input_additional').html(button);
	doSetSizes();
}

function doCloseInput() {
    $('#input_box').remove();
	$('#overlayer').remove();
	doSetSizes();
}

function createInputTextDlg() {
	var dlg = '<div id="input_box">\
	<div id="close_button" class="clearfix">\
	<input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="doCancel()"/>\
	</div>\
	<div id="input_prompt">\
	</div>\
    <div id="input_additional">\
    </div>\
	</div>';
	
	var overlayer = '<div class="overlayer" id="overlayer"></div>';
	
	$("body").prepend(dlg + overlayer);
}

function createInputCmdDlg() {
	var dlg = '<div id="input_box">\
	<div id="close_button" class="clearfix">\
	<input type="image" id="button_close" class="close" src="/static/webclient/img/button_close.png" alt="close" onclick="doCloseInput()"/>\
	</div>\
	<div id="input_prompt">\
	</div>\
    <div id="input_additional">\
    </div>\
	</div>';
	
	var overlayer = '<div class="overlayer" id="overlayer"></div>';
	
	$("body").prepend(dlg + overlayer);
}

// Callback function - called when the browser window resizes
$(window).resize(doSetSizes);
