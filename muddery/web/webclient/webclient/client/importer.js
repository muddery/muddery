
if (typeof(require) != "undefined") {
    require("../client/defines.js");

    require("../controllers/muddery_main.js");
    require("../controllers/muddery_quick_login.js");
    require("../controllers/muddery_login.js");
    require("../controllers/muddery_register.js");
    require("../controllers/muddery_password.js");
    require("../controllers/muddery_select_char.js");
    require("../controllers/muddery_message.js");
    require("../controllers/muddery_new_char.js");
    require("../controllers/muddery_scene.js");
    require("../controllers/muddery_information.js");
    require("../controllers/muddery_inventory.js");
    require("../controllers/muddery_skills.js");
    require("../controllers/muddery_quests.js");
    require("../controllers/muddery_honours.js");
    require("../controllers/muddery_object.js");
    require("../controllers/muddery_get_objects.js");
    require("../controllers/muddery_dialogue.js");
    require("../controllers/muddery_map.js");
    require("../controllers/muddery_delete_char.js");
    require("../controllers/muddery_combat.js");
    require("../controllers/muddery_combat_result.js");
    require("../controllers/muddery_confirm_combat.js");
    require("../controllers/muddery_shop.js");
    require("../controllers/muddery_goods.js");
}


import_components = function() {
    $$.main = null;
    $$.component = {};

	var views_root = "./views/";
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
};
