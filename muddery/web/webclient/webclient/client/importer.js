
// import the framework

var $$ = null;
if (parent.$$) {
	$$ = parent.$$;
}
else {
	$$ = function(str) {
    	return local_string.translate(str);
    };

	$$.text2html = text2html;
	$$.escape = escape;
	$$.commands = commands;
	$$.settings = settings;
	$$.data_handler = data_handler;
	$$.map_data = map_data;
	$$.utils = utils;
};

var controller = null;

!function() {
    // load scripts
    var public_data = ("PUBLIC" in frames_dict) ? frames_dict["PUBLIC"] : [];
    
	var begin = window.location.pathname.lastIndexOf("/");
    var name = begin < 0 ? window.location.pathname : window.location.pathname.substr(begin + 1);
    var frame_data = (name in frames_dict) ? frames_dict[name] : [];
    var scripts = public_data.scripts.concat(frame_data.scripts);
    
	for (var i in scripts) {
		$("<script>").attr("src", scripts[i])
					 .attr("type", "text/javascript")
					 .appendTo($("body"));
	}

    if (!controller && frame_data.controller) {
		// construct the controller
		var constructor = eval(frame_data.controller);
		controller = new constructor();
	
		if (controller) {
			$(document).ready(function() {
				controller.onReady();
			});
		}
	}
}();

$$.controller = $$.controller || controller;
