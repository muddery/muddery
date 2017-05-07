
var controller = {

	// message window
	clearMsgWindow: function() {
	    $("#msg_wnd>div:not(.template)").remove();
	},

	displayMsg : function(msg, type) {
        var msg_wnd = $("#msg_wnd");
        if (msg_wnd.length > 0) {
            msg_wnd.stop(true);
            msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
        }
        
        if (!type) {
        	type = "normal";
        }

		var item_template = msg_wnd.find("div.template");
		var item = item_template.clone()
			.removeClass("template")
			.addClass("msg-" + type)
        	.html(msg)
            .appendTo(msg_wnd);

        // remove old messages
        var divs = msg_wnd.find("div:not(.template)");
        var max = 40;
        var size = divs.size();
        if (size > max) {
            divs.slice(0, size - max).remove();
        }
        
        // scroll message window to bottom
        // $("#msg_wnd").scrollTop($("#msg_wnd")[0].scrollHeight);
        msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
    },
    
	// popup boxes
	showAlert: function(message) {
        controller.showMessage(_("Message"), message);
	},

	showMessage: function(header, content, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_message";
        var controller = this.getFrameController(frame_id);
        controller.setMessage(header, content, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

	showObject: function(name, icon, desc, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_object";
        var controller = this.getFrameController(frame_id);
        controller.setObject(name, icon, desc, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

    showDialogue: function(dialogues) {
        this.doClosePopupBox();

        var frame_id = "#frame_dialogue";
        var controller = this.getFrameController(frame_id);
        controller.setDialogues(dialogues, data_handler.getEscapes());

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },
    
    showShop: function(name, icon, desc, goods) {
    	this.doClosePopupBox();

        var frame_id = "#frame_shop";
        var controller = this.getFrameController(frame_id);
        controller.setShop(name, icon, desc, goods);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },
    
    showGetObjects: function(accepted, rejected) {
        // show accepted objects
        try {
            var first = true;
            for (var key in accepted) {
                if (first) {
                    controller.displayMsg(LS("You got:"));
                    first = false;
                }
                this.displayMsg(key + ": " + accepted[key]);
            }
        }
        catch(error) {
        	console.error(error.message);
        }

        // show rejected objects
        try {
            var first = true;
            for (var key in rejected) {
                if (first) {
                    controller.displayMsg(LS("You can not get:"));
                    first = false;
                }
                this.displayMsg(key + ": " + rejected[key]);
            }
        }
        catch(error) {
        	console.error(error.message);
        }

        var combat_box = $('#combat_box');
        if (combat_box.length == 0) {
            // If not in combat.
            var popup_box = $('#popup_box');
            if (popup_box.length == 0) {
                // If there is no other boxes, show getting object box.
                this.popupGetObjects(accepted, rejected);
            }
        }
        else {
            // If in combat, show objects in the combat box.
            combat.setGetObject(accepted, rejected);
        }
    },
    
    popupGetObjects: function(accepted, rejected) {
    	this.doClosePopupBox();

        var frame_id = "#frame_get_objects";
        var controller = this.getFrameController(frame_id);
        controller.setGetObjects(accepted, rejected);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },
    
    showCombat: function(combat) {     
    	this.doClosePopupBox();

        var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
        controller.reset();

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },

    closeCombat: function(data) {
        var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
        if (!controller.isCombatFinished()) {
            controller.finishCombat();
        }
    },
    
    setCombatInfo: function(desc, characters) {
        var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
        controller.setInfo(desc, characters, data_handler.character_dbref);
    },
    
    setCombatCommands: function(commands) {
    	var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
        controller.setCommands(commands);
    },
    
    setSkillResult: function(result) {
		if ("message" in result && result["message"]) {
		    var msg = text2html.parseHtml(result["message"]);
			this.displayMsg(msg);
		}
		
		var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
		controller.setSkillResult(result);
    },
    
    setSkillCD: function(skill, cd, gcd) {
    	var frame_id = "#frame_combat";
        var controller = this.getFrameController(frame_id);
		controller.setSkillCD(skill, cd, gcd);
    },
    
    finishCombat: function(result) {
    	//controller.finishCombat(result);
    },

    showGetExp: function(exp) {
        // show exp
        controller.displayMsg(LS("You got exp: ") + exp);

        var combat_box = $('#combat_box');
        if (combat_box.length > 0) {
            // If in combat, show exp in the combat box.
            combat.setGetExp(exp);
        }
    },
    
    // close popup box
    doClosePopupBox: function() {
		$("#popup_container").hide();
    	$("#popup_content").children().hide();
    },

    clearPromptBar: function() {
        $("#prompt_name").empty();
        $("#prompt_level").empty();
        $("#prompt_exp").empty();
        $("#prompt_hp").empty();
    },

    // set player's basic information
    setInfo: function(name, icon) {
        $("#prompt_name").text(name);

        var controller = this.getFrameController("#frame_information");
        controller.setInfo(name, icon);
    },

    // set player's status
    setStatus: function(level, exp, max_exp, hp, max_hp, attack, defence) {
        $("#prompt_level").text(level);

        var exp_str = "--";
        if (max_exp > 0) {
            exp_str = exp + "/" + max_exp;
        }
        $("#prompt_exp").text(exp_str);

        var hp_str = hp + "/" + max_hp;
        $("#prompt_hp").text(hp_str);

        var controller = this.getFrameController("#frame_information");
        controller.setStatus(level, exp, max_exp, hp, max_hp, attack, defence);
    },

    // set player's equipments
    setEquipments: function(equipments) {
        var controller = this.getFrameController("#frame_information");
        controller.setEquipments(equipments);
    },
    
    // set player's inventory
    setInventory: function(inventory) {
        var controller = this.getFrameController("#frame_inventory");
        controller.setInventory(inventory);
    },
    
    // set player's skills
    setSkills: function(skills) {
        var controller = this.getFrameController("#frame_skills");
        controller.setSkills(skills);
    },
    
    // set player's quests
    setQuests: function(quests) {
        var controller = this.getFrameController("#frame_quests");
        controller.setQuests(quests);
    },
    
    setScene: function(scene) {
	    var frame_id = "#frame_scene";
        var controller = this.getFrameController(frame_id);
        controller.setScene(scene);
    },

    getFrameController: function(frame_id) {
        var frame = $(frame_id);
        if (frame) {
            return frame[0].contentWindow.controller;
        }
    },
};
