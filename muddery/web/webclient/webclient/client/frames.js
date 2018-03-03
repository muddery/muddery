
var frames_dict = {
    "PUBLIC":				{scripts: 		[]},
    
    "main.html":			{scripts: 		["../controllers/base_controller.js",
                      	 	 				 "../controllers/muddery_main.js",],
                      	 	 controller:	"MudderyMain",},

    "combat_result.html":	{scripts: 		["../controllers/base_controller.js",
                      	 	 				 "../controllers/muddery_combat_result.js",],
                      	 	 controller:	"MudderyCombatResult",},

    "combat.html":			{scripts: 		["../controllers/base_controller.js",
                      	 	 				 "../controllers/muddery_combat.js",],
                      	 	 controller:	"MudderyCombat",},
                      	 	 
    "confirm_combat.html":	{scripts: 		["../controllers/base_controller.js",
                      	 					 "../controllers/muddery_confirm_combat.js",],
                      	 	 controller:	"MudderyConfirmCombat",},
            	 	 
    "delete_char.html":		{scripts: 		["../controllers/base_controller.js",
                      	    				 "../controllers/muddery_delete_char.js",],
                      	 	 controller:	"MudderyDeleteChar",},
            	 	                       	 
    "dialogue.html":		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_dialogue.js",],
                      	 	 controller:	"MudderyDialogue",},
                      	 	 
    "get_objects.html":		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_get_objects.js",],
                      	 	 controller:	"MudderyGetObjects",},
                      	 	                       	 
    "goods.html":	  	  	{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_goods.js",],
                      	 	 controller:	"MudderyGoods",},
                      	 	 
    "honours.html":	  	  	{scripts: 		["../utils/paginator.js",
    										 "../controllers/base_controller.js",
                      						 "../controllers/muddery_honours.js",],
                      	 	 controller:	"MudderyHonours",},
                      	 	 
    "information.html":		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_information.js",],
                      	 	 controller:	"MudderyInformation",},
                      	 	 
    "inventory.html":		{scripts: 		["../utils/paginator.js",
                                             "../controllers/base_controller.js",
                      						 "../controllers/muddery_inventory.js",],
                      	 	 controller:	"MudderyInventory",},
                      	 	 
    "login.html":			{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_login.js",],
                      	 	 controller:	"MudderyLogin",},
                      	 	 
    "map.html":				{scripts: 		["../libs/d3.v3.min.js",
    										 "../controllers/base_controller.js",
                      						 "../controllers/muddery_map.js",],
                      	 	 controller:	"MudderyMap",},
                      	 	                       	 
    "message.html":			{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_message.js",],
                      	 	 controller:	"MudderyMessage",},
                      	 	 
    "new_char.html":		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_new_char.js",],
                      	 	 controller:	"MudderyNewChar",},
                      	 	                       	
    "object.html":			{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_object.js",],
                      	 	 controller:	"MudderyObject",},

    "password.html":		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_password.js",],
                      	 	 controller:	"MudderyPassword",},

    "quests.html":			{scripts: 		["../utils/paginator.js",
    										 "../controllers/base_controller.js",
                      						 "../controllers/muddery_quests.js",],
                      	 	 controller:	"MudderyQuests",},
                      	 	 
	"quick_login.html":	 	{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_quick_login.js",],
                      	 	 controller:	"MudderyQuickLogin",},
                      	 	 
    "register.html": 		{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_register.js",],
                      	 	 controller:	"MudderyRegister",},
                      	 	 
    "scene.html":      	 	{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_scene.js",],
                      	 	 controller:	"MudderyScene",},
                      	 	 
	"select_char.html": 	{scripts: 		["../controllers/base_controller.js",
                      						 "../controllers/muddery_select_char.js",],
                      	 	 controller:	"MudderySelectChar",},
                      	 	 
	"shop.html": 			{scripts: 		["../utils/paginator.js",
	                                         "../controllers/base_controller.js",
                      						 "../controllers/muddery_shop.js",],
                      	 	 controller:	"MudderyShop",},
                      	 	                 
	"skills.html": 			{scripts: 		["../utils/paginator.js",
	                                         "../controllers/base_controller.js",
                      						 "../controllers/muddery_skills.js",],
                      	 	 controller:	"MudderySkills",},                      						 
}
