/*
Muddery webclient (javascript component)
*/

var combat = {
    _finished: false,
    _left: false,
    _result: null,
    _exp: null,
    _loots: null,
    _dialogue: null,

    createCombat: function(data) {
        this.closeCombat();

        var box = $('<div>')
            .attr('id', 'combat_box')
            .attr('role', 'dialog')
            .css('display', 'block')
            .addClass('modal')
            .modal({backdrop: 'static'})
            .prependTo($('#popup_container'));

        var boxDialog = $('<div>')
            .addClass('modal-dialog modal-sm')
            .addClass('vertical-center')
            .appendTo(box);

        var boxContent = $('<div>')
            .addClass('modal-content')
            .appendTo(boxDialog);

        var boxHeader = $('<div>')
            .attr('id', 'combat_desc')
            .addClass('modal-header')
            .appendTo(boxContent);

        var boxBody = $('<div>')
            .attr('id', 'combat_characters')
            .addClass('modal-body')
            .css('min-height', '100px')
            .appendTo(boxContent);

        var boxFooter = $('<div>')
            .attr('id', 'combat_commands')
            .attr('class', 'modal-footer').appendTo(boxContent);

        // reset combat data
        data_handler.current_target = "";
        this._finished = false;
        this._left = false;
        this._result = null;
        this._exp = null;
        this._loots = null;
        this._dialogue = null;

        webclient.doSetPopupSize();
    },

    setGetObject: function(data) {
        this._loots = data;
    },

    displayGetObject: function(data) {
        // object's info
        var boxBodyLoot = $('#combat_loot');
        if (boxBodyLoot.length > 0) {
            // add object's name
            try {
                var accepted = data.accepted;
                var get = false;
                for (var key in accepted) {
                    get = true;
                    $('<div>')
                        .text(key + ": " + accepted[key])
                        .appendTo(boxBodyLoot);
                }

                if (get) {
                    $('<div>')
                        .text(LS('You got:'))
                        .prependTo(boxBodyLoot);
                }
            }
            catch(error) {
            }

            try {
                var rejected = data.rejected;
                for (var key in rejected) {
                    $('<div>')
                        .text(key + ": " + rejected[key])
                        .appendTo(boxBodyLoot);
                }
            }
            catch(error) {
            }
        }
    },

    setGetExp: function(data) {
        this._exp = data;
    },

    displayGetExp: function(data) {
        var boxBodyExp = $('#combat_exp');
        if (boxBodyExp.length > 0) {
            $('<div>')
                .text(LS('You got exp: ') + data)
                .appendTo(boxBodyExp);
        }
    },

    finishCombat: function(data) {
        this._finished = true;
        this._result = data;
    },

    leftCombat: function(data) {
        this._left = true;
        setTimeout(combat.showCombatResult, 500);
    },

    showCombatResult: function() {
        var self = combat;

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

    closeCombat: function() {
        if ($('#popup_box').size() == 0) {
            $('.modal-backdrop').remove();
        }
        if ($('#combat_box').size() > 0){
            $('#combat_box').remove();
            $('.modal-backdrop').remove();
        }

        // show dialogue after combat
        if (this._dialogue) {
            webclient.displayDialogue(this._dialogue);
            this._dialogue = null;
        }
    },

    displayCombatInfo: function(data) {
        var desc = $('#combat_desc');
        desc.text(data.desc);

        var team = 0;
        var enemy = 0;
        var top = 10;
        var line_height = 30;
        var characters = $('#combat_characters');
        for (var i in data.characters) {
            var fighter = data.characters[i];
            var div = $('<div>').attr('id', 'fighter_' + fighter.dbref.slice(1))
                                .data('dbref', fighter.dbref);

            $('<div>').attr('id', 'status_' + fighter.dbref.slice(1))
                      .text(fighter.hp + '/' + fighter.max_hp)
                      .appendTo(div);

            if ("icon" in fighter && fighter["icon"]) {
                var url = settings.resource_location + fighter["icon"];
                var icon = $("<div>")
                    .append($("<img>")
                        .attr("src", url)
                        .addClass("fighter_icon"))
                    .appendTo(div);
            }

            div.append(fighter.name);
            
            if (fighter.dbref == data_handler.character_dbref) {
                div.addClass('fighter_team')
                   .css('top', top + team * line_height);
                team++;
            }
            else {
                div.addClass("fighter_enemy")
                   .css('top', top + enemy * line_height);
                enemy++;
                if (!data_handler.current_target) {
                    data_handler.current_target = fighter.dbref;
                }
            }

            data_handler.name_list[fighter.dbref] = fighter.name;
            
            div.appendTo(characters);
        }
    },

    displayCombatCommands: function(data) {
        var commands = $('#combat_commands');
        if (commands) {
            var content = $('<div>').attr('id', 'combat_btns');
            for (var i in data) {
                var command = data[i];
                var button = $('<button>')
                    .addClass('btn-combat')
                    .attr('type', 'button')
                    .attr('key', command.key)
                    .attr('id', 'combat_btn_' + command.key)
                    .attr('onclick', 'combat.doCombatSkill(this); return false;')
                    .data("cd", 0)
                    .css({'left': 20 + i * 80});

                var img = $("<img>").addClass("command_icon");

                if ("icon" in command && command["icon"]) {
                    var url = settings.resource_location + command["icon"];
                    img.attr("src", url);
                }

                var icon = $("<center>")
                        .append(img)
                        .appendTo(button);

                button.append($("<div>")
                    .addClass('combat-skill-name')
                    .text(command.name));

                button.append($("<div>").addClass('cooldown'));
                button.appendTo(content);
            }
            
            commands.html(content);

            this.displaySkillCD();
        }
    },

    displayStatus: function(data) {
        for (var i in data) {
            var character = $('#status_' + data[i]["dbref"].slice(1));
            if (character.length > 0) {
                character.text(data[i]["hp"] + '/' + data[i]["max_hp"])
            }
        }
    },

    displaySkillResult: function(skill) {

		/*
		if (data[i].type == "joined") {
			var result = $('#fighter_' + data[i].dbref.slice(1));
			if (result.length == 0) {
				var fighter = data[i];
				var div = $('<div>').attr('id', 'fighter_' + fighter.dbref.slice(1))
									.text(fighter.name)
									.data('dbref', fighter.dbref);
				$('<div>').addClass('hp')
						  .attr('id', 'status_' + fighter.dbref.slice(1))
						  .text(fighter.hp + '/' + fighter.max_hp)
						  .appendTo(div);
				
				if (fighter.dbref == data_handler.character_dbref) {
					div.addClass("fighter_team");
				}
				else {
					div.addClass("fighter_enemy");
					if (!data_handler.current_target) {
						data_handler.current_target = fighter.dbref;
					}
				}
				
				var characters = $('#combat_characters');
				div.appendTo(characters);
			}
		}
		else */

		if (skill.key == "skill_normal_hit" ||
		    skill.key == "skill_dunt") {
			var caller = $('#fighter_' + skill.caller.slice(1));
			if (skill.caller == data_handler.character_dbref) {
				caller.animate({left: '50%'}, 100);
				caller.animate({left: '12%'}, 100);
			}
			else {
				caller.animate({right: '50%'}, 100);
				caller.animate({right: '12%'}, 100);
			}
			
			// var target = $('#status_' + data[i].target.slice(1));
			// target.text(data[i].hp + '/' + data[i].max_hp)
		}
		else if (skill.key == "skill_normal_heal" ||
		         skill.key == "skill_powerful_heal") {
			// var target = $('#status_' + data[i].target.slice(1));
			// target.text(data[i].hp + '/' + data[i].max_hp)
		}
		else if (skill.key == "skill_escape") {
			if (skill.effect == 1) {
				var character = $('#status_' + skill.target.slice(1));
				if (character.length > 0) {
				    character.text(LS("Escaped"));
				}
			}
		}
	
        // Update status.
        if ("status" in skill) {
            this.displayStatus(skill["status"]);
        }
    },

    displaySkillCD: function() {
        $('#combat_btns button').each(function(){
            combat.setButtonCD($(this));
        });
    },

    setButtonCD: function(btn) {
        var key = btn.attr('key');

        var cd_time = 0;
        if (key in data_handler.skill_cd_time) {
            cd_time = data_handler.skill_cd_time[key];
        }

        var current_cd = btn.data("cd");
        if (current_cd >= cd_time) {
            return;
        }

        var current_time = (new Date()).valueOf();

        $('div.cooldown', btn).stop(true, true);
        if (current_cd < current_time) {
            // set a new cd
            $('div.cooldown', btn).css('height', '100%')
                                  .css('top', 0);
        }
        $('div.cooldown', btn).animate({height: '0%', top: '100%'}, cd_time - current_time, 'linear');
        btn.data("cd", cd_time);
    },
    
    doCombatSkill: function(caller) {
        if (this._finished) {
            return;
        }

        var key = $(caller).attr('key');
        commands.doCastSkill(key)
    },

    isCombatFinished: function() {
        return this._finished;
    },
    
    isLeftCombat: function() {
    	return this._left;
    },

    setDialogue: function(data) {
        this._dialogue = data;
    },
}
