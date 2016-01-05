/*
Muddery webclient (javascript component)
*/

var combat = {
    _self_dbref: null,
    _name_dict: {},
    _current_target: null,
    _finished: false,
    _result: null,
    _loot: null,
    _exp: 0,
    _skill_cd_time: {},
    _dialogue: null,
    
    setSelf: function(dbref) {
        this._self_dbref = dbref;
    },

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
        this._current_target = null;
        this._finished = false;
        this._result = null;
        this._loot = null;
        this._exp = 0;
        this._skill_cd_time = {};
        this._dialogue = null;

        webclient.doSetPopupSize();
    },

    displayGetObject: function(data) {
        this._loot = data;
    },

    displayGetExp: function(data) {
        this._exp = data;
    },

    finishCombat: function(data) {
        this._finished = true;
        this._result = data;
        
        setTimeout(combat.showCombatResult, 1000);
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

        var get = false;

        // exp
        if (self._exp > 0) {
            $('<div>')
                .text(LS('Exp') + LS(': ') + self._exp)
                .appendTo(boxBodyLoot);
            get = true;
        }

        // object's info
        if (self._loot) {
            // add object's name
            try {
                var accepted = self._loot.accepted;
                if (accepted.length > 0) {
                    get = true;
                }
                for (var key in accepted) {
                    $('<div>')
                        .text(key + ": " + accepted[key])
                        .appendTo(boxBodyLoot);
                }
            }
            catch(error) {
            }

            try {
                var rejected = self._loot.rejected;
                for (var key in rejected) {
                    $('<div>')
                        .text(key + ": " + rejected[key])
                        .appendTo(boxBodyLoot);
                }
            }
            catch(error) {
            }
        }

        if (get) {
            $('<div>')
                .text(LS('You got:'))
                .prependTo(boxBodyLoot);
        }

        // result
        if ("stopped" in self._result) {
            boxBodyResult.text(LS("Combat stopped !"));
        }
        else if ("escaped" in self._result) {
            boxBodyResult.text(LS("Escaped !"));
        }
        else if ("winner" in self._result) {
            var win = false;
            for (var i in self._result.winner) {
                if (self._result.winner[i].dbref == self._self_dbref) {
                    win = true;
                    break;
                }
            }

            if (win) {
                boxBodyResult.text(LS("You win !"));
            }
            else {
                boxBodyResult.text(LS("You lost !"));
            }
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
                                .text(fighter.name)
                                .data('dbref', fighter.dbref);

            $('<div>').attr('id', 'status_' + fighter.dbref.slice(1))
                      .text(fighter.hp + '/' + fighter.max_hp)
                      .prependTo(div);
            
            if (fighter.dbref == this._self_dbref) {
                div.addClass('fighter_team')
                   .css('top', top + team * line_height);
                team++;
            }
            else {
                div.addClass("fighter_enemy")
                   .css('top', top + enemy * line_height);
                enemy++;
                if (!this._current_target) {
                    this._current_target = fighter.dbref;
                }
            }

            this._name_dict[fighter.dbref] = fighter.name;
            
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
                    .addClass('btn btn-default')
                    .attr('type', 'button')
                    .attr('key', command.key)
                    .attr('id', 'combat_btn_' + command.key)
                    .attr('onclick', 'combat.doCombatSkill(this); return false;')
                    .css({'left': 20 + i * 90});

                button.append($("<div>").text(command.name));

                button.append($("<div>").addClass('cooldown'));
                
                button.appendTo(content);
            }
            
            commands.html(content);

            $('#combat_commands').css({'height': 60});
        }
    },

    displayCombatProcess: function(data) {
        for (var i in data) {
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
                    
                    if (fighter.dbref == this._self_dbref) {
                        div.addClass("fighter_team");
                    }
                    else {
                        div.addClass("fighter_enemy");
                        if (!this._current_targ) {
                            this._current_target = fighter.dbref;
                        }
                    }
                    
                    var characters = $('#combat_characters');
                    div.appendTo(characters);
                }
            }
            else */
            if (data[i].type == "attacked") {
                var caller = $('#fighter_' + data[i].caller.slice(1));
                if (data[i].caller == this._self_dbref) {
                    caller.animate({left: '50%'}, 100);
                    caller.animate({left: '12%'}, 100);
                }
                else {
                    caller.animate({right: '50%'}, 100);
                    caller.animate({right: '12%'}, 100);
                }
                
                var target = $('#status_' + data[i].target.slice(1));
                target.text(data[i].hp + '/' + data[i].max_hp)
            }
            else if (data[i].type == "healed") {
                var target = $('#status_' + data[i].target.slice(1));
                target.text(data[i].hp + '/' + data[i].max_hp)
            }
            else if (data[i].type == "escape") {
                if (data[i].success) {
                    var target = $('#status_' + data[i].caller.slice(1));
                    target.text(LS("Escaped"));
                }

                if (data[i].caller in this._name_dict) {
                    var name = "";
                    if (data[i].caller == this._self_dbref) {
                        name = LS("You");
                    }
                    else {
                        name = this._name_dict[data[i].caller];
                    }

                    if (data[i].success) {
                        webclient.displayMsg("{c" + name + "{n" + LS(" escaped from the combat."));
                    }
                    else {
                        webclient.displayMsg("{c" + name + "{n" + LS(" failed to escape."));
                    }
                }
            }
        }
        
        /*
        var fighter = $('status_' + data["character"]);
        if (fighter) {
            fighter.text(data["hp"] + '/' + data["max_hp"]).appendTo(div);
        }
        */
    },

    displaySkillCD: function(data) {
        // set skill's cd
        var cd = data["cd"];
        var gcd = data["gcd"];
        var key = data["skill"];
        var btn = $('#combat_btn_' + key);

        $('#combat_btns button').each(function(){
            var time = gcd;
            if (this == btn[0]) {
                if (cd > gcd) {
                    time = cd;
                }
            }
            combat.setButtonCD($(this), time);
        });
    },

    setButtonCD: function(btn, cd) {
        var key = btn.attr('key');
        var current_time = (new Date()).valueOf();
        var cd_time = current_time + cd * 1000;

        var current_cd_time = combat._skill_cd_time[key];
        if (!current_cd_time) {
            current_cd_time = 0;
        }

        if (current_cd_time >= cd_time) {
            return;
        }

        $('div.cooldown', btn).stop(true, true);
        if (current_cd_time < current_time) {
            $('div.cooldown', btn).width('100%');
        }
        $('div.cooldown', btn).animate({width: '0%'}, cd * 1000, 'linear');

        combat._skill_cd_time[key] = cd_time;
    },
    
    doCombatSkill: function(caller) {
        if (this._finished) {
            return;
        }

        var key = $(caller).attr('key');
        var cd_time = this._skill_cd_time[key];
        if (cd_time) {
            var current_time = (new Date()).valueOf();
            if (cd_time > current_time) {
                return;
            }
        }

        commands.doCombatSkill(caller)
    },

    isInCombat: function() {
        return this._finished;
    },

    getCurrentTarget: function() {
        return this._current_target;
    },

    setDialogue: function(data) {
        this._dialogue = data;
    },
}