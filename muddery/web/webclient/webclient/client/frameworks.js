
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

$$.frameworks = {
    main:			        {ctrler_name:	"MudderyMain"},

    components: {
        quick_login:	    	{ctrler_name:	"MudderyQuickLogin",
                                 view:          "quick_login.html"},

        login:					{ctrler_name:	"MudderyLogin",
                                 view:          "login.html"},

        register:				{ctrler_name:	"MudderyRegister",
                                 view:          "register.html"},

        password:				{ctrler_name:	"MudderyPassword",
                                 view:          "password.html"},

        select_char:			{ctrler_name:	"MudderySelectChar",
                                 view:          "select_char.html"},

        message:				{ctrler_name:	"MudderyMessage",
                                 view:          "message.html"},

        new_char:				{ctrler_name:	"MudderyNewChar",
                                 view:          "new_char.html"},

        scene:					{ctrler_name:	"MudderyScene",
                                 view:          "scene.html"},

        information:			{ctrler_name:	"MudderyInformation",
                                 view:          "information.html"},

        inventory:				{ctrler_name:	"MudderyInventory",
                                 view:          "inventory.html"},

        skills:    				{ctrler_name:	"MudderySkills",
                                 view:          "skills.html"},

        quests:    				{ctrler_name:	"MudderyQuests",
                                 view:          "quests.html"},

        honours:    			{ctrler_name:	"MudderyHonours",
                                 view:          "honours.html"},

        object:    				{ctrler_name:	"MudderyObject",
                                 view:          "object.html"},

        get_objects:    		{ctrler_name:	"MudderyGetObjects",
                                 view:          "get_objects.html"},

        dialogue:	    		{ctrler_name:	"MudderyDialogue",
                                 view:          "dialogue.html"},

        map:		    		{ctrler_name:	"MudderyMap",
                                 view:          "map.html"},

        delete_char:			{ctrler_name:	"MudderyDeleteChar",
                                 view:          "delete_char.html"},

        combat:					{ctrler_name:	"MudderyCombat",
                                 view:          "combat.html"},

        combat_result:			{ctrler_name:	"MudderyCombatResult",
                                 view:          "combat_result.html"},

        confirm_combat:			{ctrler_name:	"MudderyConfirmCombat",
                                 view:          "confirm_combat.html"},

        shop:					{ctrler_name:	"MudderyShop",
                                 view:          "shop.html"},

        goods:					{ctrler_name:	"MudderyGoods",
                                 view:          "goods.html"},
    }
}
