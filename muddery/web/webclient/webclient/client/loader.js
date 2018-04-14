
// load the framework

if (typeof(require) != "undefined") {
    require("../client/defines.js");
    require("../lang/local_string.js");
    require("../utils/text2html.js");
    require("../utils/text_escape.js");
    require("../client/frameworks.js");
}


!function() {
    $$.local_string.setLanguage(settings.default_language);
    $$.text2html = new Text2HTML();
    $$.text_escape = new TextEscape();

    // get main controller
    var constructor = eval($$.frameworks.main.ctrler_name);
	$$.main = new constructor($("#frame_main"));

    $$.component = {};
	var components_root = "./views/";
	var ajax = (typeof(require) == "undefined");

	for (var key in $$.frameworks.components) {
		var component_info = $$.frameworks.components[key];

		var div = $("#frame_" + key);
		if (div.length > 0) {
			if (ajax && component_info.view) {
				// load frame
				$.ajax({url: components_root + component_info.view,
						context: key,
						success: function(result) {
								var key = this;
								var component_info = $$.frameworks.components[key];

								var div = $("#frame_" + key);
								div.html($("<div>").html(result))
								   .hide();

								var constructor = eval(component_info.ctrler_name);
								$$.component[key] = new constructor(div);
								$$.component[key].onReady();

								if (Object.keys($$.component).length == Object.keys($$.frameworks.components).length) {
								    $$.main.onReady();
								    $$.client.onReady();
								}
							}
						});
			}
			else {
				var constructor = eval(component_info.ctrler_name);
				$$.component[key] = new constructor(div);
				$$.component[key].onReady();

				if (Object.keys($$.component).length == Object.keys($$.frameworks.components).length) {
				    $$.main.onReady();
					$$.client.onReady();
				}
			}
		}
	}
}();
