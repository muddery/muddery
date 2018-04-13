
if (typeof(require) != "undefined") {
    require("../client/defines.js");
}

$$.frameworks = {
    main:			        {scripts: 		[],
                      	 	 ctrler_name:	"MudderyMain"},

    components: {
        quick_login:	    	{scripts: 		[],
                                 ctrler_name:	"MudderyQuickLogin",
                                 view:          "quick_login.html"},

        login:					{scripts: 		[],
                                 ctrler_name:	"MudderyLogin",
                                 view:          "login.html"},

        register:				{scripts: 		[],
                                 ctrler_name:	"MudderyRegister",
                                 view:          "register.html"},

        password:				{scripts: 		[],
                                 ctrler_name:	"MudderyPassword",
                                 view:          "password.html"},

        select_char:			{scripts: 		[],
                                 ctrler_name:	"MudderySelectChar",
                                 view:          "select_char.html"},

        message:				{scripts: 		[],
                                 ctrler_name:	"MudderyMessage",
                                 view:          "message.html"},

        new_char:				{scripts: 		[],
                                 ctrler_name:	"MudderyNewChar",
                                 view:          "new_char.html"},

        scene:					{scripts: 		[],
                                 ctrler_name:	"MudderyScene",
                                 view:          "scene.html"},

        information:			{scripts: 		[],
                                 ctrler_name:	"MudderyInformation",
                                 view:          "information.html"},

        inventory:				{scripts: 		[],
                                 ctrler_name:	"MudderyInventory",
                                 view:          "inventory.html"},

        skills:    				{scripts: 		[],
                                 ctrler_name:	"MudderySkills",
                                 view:          "skills.html"},

        quests:    				{scripts: 		[],
                                 ctrler_name:	"MudderyQuests",
                                 view:          "quests.html"},

        honours:    			{scripts: 		[],
                                 ctrler_name:	"MudderyHonours",
                                 view:          "honours.html"},

        object:    				{scripts: 		[],
                                 ctrler_name:	"MudderyObject",
                                 view:          "object.html"},

        get_objects:    		{scripts: 		[],
                                 ctrler_name:	"MudderyGetObjects",
                                 view:          "get_objects.html"},

        dialogue:	    		{scripts: 		[],
                                 ctrler_name:	"MudderyDialogue",
                                 view:          "dialogue.html"},

        map:		    		{scripts: 		[],
                                 ctrler_name:	"MudderyMap",
                                 view:          "map.html"},

        delete_char:			{scripts: 		[],
                                 ctrler_name:	"MudderyDeleteChar",
                                 view:          "delete_char.html"},

        combat:					{scripts: 		[],
                                 ctrler_name:	"MudderyCombat",
                                 view:          "combat.html"},

        combat_result:			{scripts: 		[],
                                 ctrler_name:	"MudderyCombatResult",
                                 view:          "combat_result.html"},

        confirm_combat:			{scripts: 		[],
                                 ctrler_name:	"MudderyConfirmCombat",
                                 view:          "confirm_combat.html"},

        shop:					{scripts: 		[],
                                 ctrler_name:	"MudderyShop",
                                 view:          "shop.html"},

        goods:					{scripts: 		[],
                                 ctrler_name:	"MudderyGoods",
                                 view:          "goods.html"},
    }
}
