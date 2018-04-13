
if (typeof(require) != "undefined") {
    require("../client/defines.js");
}

$$.main = null;
$$.component = {};

!function() {
	var views_root = "../views/";
	var ajax = (typeof(require) == "undefined");

	var constructor = eval($$.frameworks.main.ctrler_name);
	$$.main = new constructor(div);

	for (var key in $$.frameworks.components) {
		var component_info = $$.frameworks.components[key];

		var div = $("#frame_" + key);
		if (div.length > 0) {
			if (ajax && component_info.view) {
				// load frame
				$.ajax({url: views_root + component_info.view,
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
					$$.client.onReady();
				}
			}
		}
	}
}();
