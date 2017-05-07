
var controller = {

	_self_dbref: "",
	_target: "",
	_combat_finished: false,
	_skill_cd_time: {},

    // close popup box
    doClosePopupBox: function() {
        parent.controller.doClosePopupBox();
    },
    
    reset: function() {
		$("#desc").empty();
	
    	// Remove characters that are not template.
    	$("#characters>:not(.template)").remove();
    	
    	// Remove skill buttons that are not template.
    	$("#buttons>:not(.template)").remove();
    	
    	this._self_dbref = "";
    	this._target = "";
		this._combat_finished = false;
    },

	setInfo: function(desc, characters, self_dbref) {
		if (this._combat_finished) {
			return;
		}
		
	    this._self_dbref = self_dbref;
	    
	    var self_team = "";
	    for (var i in characters) {
	    	if (characters[i]["dbref"] == self_dbref) {
	    		self_team = characters[i]["team"];
	    	}
	    }
	    
		// add desc
	    desc = text2html.parseHtml(desc);
	    $("#desc").html(desc);
	    
	    // add characters
	    var container = $("#characters");

		var teammate_number = 0;
		var enemy_number = 0;
        var top = 10;
        var line_height = 30;
        
		var item_template = $("#characters>.template");
		for (var i in characters) {
			var character = characters[i];
			
			var item = item_template.clone()
           		.removeClass("template")
           		.attr("id", "char_" + character["dbref"].slice(1))
           		.data("dbref", character["dbref"]);
           	
           	item.find(".status").text(character["hp"] + "/" + character["max_hp"]);
           	
           	if (character["icon"]) {
           		item.find(".img_icon").attr("src", settings.resource_location + character["icon"]);
           		item.find(".div_icon").show();
           	}
           	else {
           		item.find(".div_icon").hide();
           	}
           		
           	item.find(".name").text(character["name"]);
           	
           	if (character["team"] == self_team) {
                item.addClass("teammate")
                   .css('top', top + teammate_number * line_height);
                teammate_number++;
            }
            else {
                item.addClass("enemy")
                   .css('top', top + enemy_number * line_height);
                enemy_number++;
                
                if (!this._target) {
                	// Set default target.
                    this._target = character["dbref"];
                }
            }
            
            item.appendTo(container);
		}
	},

	setCommands: function(commands) {
		var container = $('#buttons');
		var item_template = container.find("button.template");

		if (commands) {
            for (var i in commands) {
                var command = commands[i];
                
                var item = item_template.clone()
                    .removeClass("template")
                    .attr("id", "cmd_" + command["key"])
                    .data("key", command["key"])
                    .data("cd", 0)
                    .css({"left": 20 + i * 80});
                    
                if (command["icon"]) {
                    item.find(".command_icon").attr("src", settings.resource_location + command["icon"]);
                }

                var name = text2html.parseHtml(command["name"]);
                item.find(".command_name").html(name);
                
                item.appendTo(container);
            }
        }
    },

    setSkillResult: function(result) {
		if (this._combat_finished) {
			return;
		}
			
		if (skill.key == "skill_normal_hit" ||
		    skill.key == "skill_dunt") {

			var caller = $('#char_' + skill.caller.slice(1));
			if (caller.hasClass("teammate")) {
				caller.animate({left: '50%'}, 100);
				caller.animate({left: '12%'}, 100);
			}
			else {
				caller.animate({right: '50%'}, 100);
				caller.animate({right: '12%'}, 100);
			}
		}
		else if (skill.key == "skill_normal_heal" ||
		         skill.key == "skill_powerful_heal") {
		}
		else if (skill.key == "skill_escape") {
			if (skill.effect == 1) {
				var item_id = "#char_" + skill["target"].slice(1) + ".status";
				$(item_id).text(LS("Escaped"));
			}
		}
	
        // Update status.
        if ("status" in skill) {
            this.updateStatus(skill["status"]);
        }
    },
    
    updateStatus: function(status) {
        for (var i in status) {
            var item_id = "#char_" + status[i]["dbref"].slice(1) + ".status";
            $(item_id).text(status[i]["hp"] + "/" + status[i]["max_hp"])
        }
    },
    
    setSkillCD: function(skill, cd, gcd) {
    	if (this._combat_finished) {
			return;
		}
		
        // update skill's cd
        var current_time = (new Date()).valueOf();

        // cd_time in milliseconds
        var cd_time = current_time + cd * 1000;
        if (skill in this._skill_cd_time) {
            if (this._skill_cd_time[skill] < cd_time) {
                this._skill_cd_time[skill] = cd_time;
            }
        }

        var gcd_time = current_time + gcd * 1000;
        for (var key in this._skill_cd_time) {
            if (this._skill_cd_time[key] < gcd_time) {
                this._skill_cd_time[key] = gcd_time;
            }
        }

        this.showSkillCD();
    },
    
    showSkillCD: function() {
        $("#buttons>button").each(function() {
            controller.showButtonCD(this);
        });
    },

    showButtonCD: function(button_id) {
    	var button = $(button_id);
    	var cooldown = button.find(">.cooldown");
    	
        var key = button.data("key");

        var cd_time = 0;
        if (key in _skill_cd_time) {
            cd_time = _skill_cd_time[key];
        }

        var current_cd = button.data("cd");
        if (current_cd >= cd_time) {
            return;
        }

        var current_time = (new Date()).valueOf();

        cooldown.stop(true, true);
        if (current_cd < current_time) {
            // set a new cd
            cooldown.css("height", "100%")
                .css("top", 0);
        }
        
        cooldown.animate({height: "0%", top: "100%"}, cd_time - current_time, "linear");
        btn.data("cd", cd_time);
    },

    doCombatSkill: function(caller) {
        if (this._finished) {
            return;
        }
        
        if (skill in _skill_cd_time) {
            var cd_time = _skill_cd_time[skill];
            var current_time = (new Date()).valueOf();
            if (cd_time > current_time) {
                return;
            }
        }

        var key = $(caller).data('key');
        parent.commands.doCastSkill(key)
    },
    
    finishCombat: function(result) {
        this._finished = true;
        this._result = result;
        setTimeout(controller.showCombatResult, 750);
    },
    
    isCombatFinished: function() {
        return this._finished;
    },

    showCombatResult: function() {
        var self = controller;

        $('#combat_desc').remove();
        $('#combat_characters').remove();
        $('#combat_commands').remove();
        
        var box = $('#combat_box').empty();

        var boxDialog = $('<div>')
            .addClass('modal-dialog modal-sm')
            .addClass('vertical-center')
            .appendTo(box);

        var boxContent = $('<div>')
            .addClass('modal-content')
            .appendTo(boxDialog);

        var boxHeader = $('<div>')
            .attr('id', 'combat_messages')
            .addClass('modal-header')
            .appendTo(boxContent);

        var boxBodyResult = $('<div>')
            .attr('id', 'combat_result')
            .addClass('modal-body')
            .appendTo(boxContent);

        var boxBodyExp = $('<div>')
            .attr('id', 'combat_exp')
            .addClass('modal-body')
            .appendTo(boxContent);
            
        var boxBodyLoot = $('<div>')
            .attr('id', 'combat_loot')
            .addClass('modal-body')
            .appendTo(boxContent);

        var boxFooter = $('<div>')
            .addClass('modal-footer')
            .appendTo(boxContent);

        $('<center>')
            .append($('<h4>')
                .addClass('modal-title')
                .text(LS('BATTLE RESULT')).appendTo(boxHeader));

        // result
        if ("escaped" in self._result) {
            boxBodyResult.text(LS("Escaped !"));
        }
        else if ("win" in self._result) {
            boxBodyResult.text(LS("You win !"));
        }
        else if ("lose" in self._result) {
            boxBodyResult.text(LS("You lost !"));
        }

        if (self._exp) {
            self.displayGetExp(self._exp);
        }

        if (self._loots) {
            self.displayGetObject(self._loots);
        }

        // button
        var center = $('<center>');
        var button = $('<button>')
            .addClass('btn btn-default')
            .attr('type', 'button')
            .attr('id', 'button_center')
            .attr('onClick', 'combat.closeCombat()')
            .text(LS('OK'))
            .addClass('btn btn-primary');

        button.appendTo(center);
        center.appendTo(boxFooter);

        webclient.doSetPopupSize();
    },
};
