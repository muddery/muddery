
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
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setMessage(header, content, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

	showObject: function(name, icon, desc, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_object";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setObject(name, icon, desc, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

    setDialogueList: function(data) {
        if (data.length == 0) {
            this.doClosePopupBox();
        }
        else {
            if ($("#frame_combat").is(":visible")) {
                // show dialogue after a combat
        		var frame_id = "#frame_combat_result";
				var result_ctrl = this.getFrameController(frame_id);
				result_ctrl.setDialogue(data);
            }
            else {
                data_handler.dialogues_list = data;
                dialogues = data_handler.dialogues_list.shift();
                if (dialogues.length > 0) {
                    data_handler.dialogue_target = dialogues[0].npc;
                }
                this.showDialogue(dialogues);
            }
        }
    },

    showDialogue: function(dialogues) {
        this.doClosePopupBox();

        var frame_id = "#frame_dialogue";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setDialogues(dialogues, data_handler.getEscapes());

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },
    
    showShop: function(name, icon, desc, goods) {
    	this.doClosePopupBox();

        var frame_id = "#frame_shop";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setShop(name, icon, desc, goods);

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
                    this.displayMsg(LS("You got:"));
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
                    this.displayMsg(LS("You can not get:"));
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
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setGetObjects(accepted, rejected);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },
    
    showCombat: function(combat) {     
    	this.doClosePopupBox();

        var combat_id = "#frame_combat";
        var combat_ctrl = this.getFrameController(combat_id);
        combat_ctrl.reset(data_handler.skill_cd_time);
        
        var result_id = "#frame_combat_result";
		var result_ctrl = this.getFrameController(result_id);
		result_ctrl.clear();

        $(combat_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
    },

    closeCombat: function(data) {
        var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        if (!frame_ctrl.isCombatFinished()) {
            frame_ctrl.finishCombat();
        }
    },
    
    setCombatInfo: function(desc, characters) {
        var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setInfo(desc, characters, data_handler.character_dbref);

        webclient.doSetVisiblePopupSize();
    },
    
    setCombatCommands: function(commands) {
    	var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setCommands(commands);
    },
    
    setSkillResult: function(result) {
		if ("message" in result && result["message"]) {
		    var msg = text2html.parseHtml(result["message"]);
			this.displayMsg(msg);
		}
		
		var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setSkillResult(result);
    },
    
    setSkillCD: function(skill, cd, gcd) {
    	data_handler.setSkillCD(skill, cd, gcd);
    	
    	var frame_id = "#frame_combat";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setSkillCD(skill, cd, gcd);
    },
    
    finishCombat: function(result) {
		var combat_id = "#frame_combat";
		var combat_ctrl = this.getFrameController(combat_id);
		combat_ctrl.finishCombat();

		var result_id = "#frame_combat_result";
		var result_ctrl = this.getFrameController(result_id);
		result_ctrl.setResult(result);

        setTimeout(this.showCombatResult, 750);
    },
    
    showCombatResult: function() {
		var self = this;
		
    	$("#popup_content").children().hide();
        $("#frame_combat_result").show();
        webclient.doSetVisiblePopupSize();
    },

    showGetExp: function(exp) {
        // show exp
        this.displayMsg(LS("You got exp: ") + exp);

        var frame_id = "#frame_combat_result";
        var frame_ctrl = this.getFrameController(frame_id);
		frame_ctrl.setGetExp(exp);
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

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setInfo(name, icon);
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

        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setStatus(level, exp, max_exp, hp, max_hp, attack, defence);
    },

    // set player's equipments
    setEquipments: function(equipments) {
        var frame_ctrl = this.getFrameController("#frame_information");
        frame_ctrl.setEquipments(equipments);
    },
    
    // set player's inventory
    setInventory: function(inventory) {
        var frame_ctrl = this.getFrameController("#frame_inventory");
        frame_ctrl.setInventory(inventory);
    },
    
    // set player's skills
    setSkills: function(skills) {
        var frame_ctrl = this.getFrameController("#frame_skills");
        frame_ctrl.setSkills(skills);
    },
    
    // set player's quests
    setQuests: function(quests) {
        var frame_ctrl = this.getFrameController("#frame_quests");
        frame_ctrl.setQuests(quests);
    },
    
    setScene: function(scene) {
	    var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.setScene(scene);
    },

    showObjMovedIn: function(objects) {
        var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.addObjects(objects);
    },

    showObjMovedOut: function(objects) {
        // If the player is talking to it, close the dialog window.
        if ($("#frame_dialogue").is(":visible")) {
            for (var key in objects) {
                for (var i in objects[key]) {
                    var dbref = objects[key][i]["dbref"];
                    if (data_handler.dialogue_target == dbref) {
                        this.doClosePopupBox();
                        break;
                    }
                }
            }
        }

        // remove objects from scene
        var frame_id = "#frame_scene";
        var frame_ctrl = this.getFrameController(frame_id);
        frame_ctrl.removeObjects(objects);
    },

    getFrameController: function(frame_id) {
        var frame = $(frame_id);
        if (frame.length > 0) {
            return frame[0].contentWindow.controller;
        }
    },
};
