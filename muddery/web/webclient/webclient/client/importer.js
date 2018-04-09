
// import the framework

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

var controller = null;

!function() {
	var views_root = "../views/";
	var ajax = (typeof(require) == "undefined");

	for (var key in frameworks) {
		var frame_info = frameworks[key];

		var div = $("#" + key);
		if (div.length > 0) {
			if (ajax && frame_info.view) {
				// load frame
				$.ajax({url: views_root + frame_info.view,
						context: key,
						success: function(result) {
								var key = this;
								var frame_info = frameworks[key];
								var div = $("#" + key);
								div.html($("<div>").html(result));
								var constructor = eval(frame_info.ctrler_name);
								frame_info.controller = new constructor(div);
								frame_info.controller.onReady();
							}
						});
			}
			else {
				var constructor = eval(frame_info.ctrler_name);
				frame_info.controller = new constructor(div);
				frame_info.controller.onReady();
			}
		}
	}

	controller = frameworks["body"].controller;
}();

$$.controller = controller;

