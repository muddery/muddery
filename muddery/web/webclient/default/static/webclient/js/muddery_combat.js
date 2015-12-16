/*
Muddery webclient (javascript component)
*/

var combat = {
    _self_dbref: null,
    _current_target: null,
    _finished: false,
    _result: null,
    _loot: null,
    _skill_cd_time: {},
    
    setSelf: function(dbref) {
        this._self_dbref = dbref;
    },

    createCombat: function(data) {
        this.closeCombat();

        var box = $('<div>').attr('id', 'combat_box');

        box.attr('class', 'modal fade');
        box.attr('style', 'display: block; padding-left: 15px;');
        box.attr('role', 'dialog');

        var boxDialog = $('<div>').attr('class', 'modal-dialog modal-lg').appendTo(box);
        var boxContent = $('<div>').attr('class', 'modal-content').appendTo(boxDialog);

        var boxHeader = $('<div>')
            .attr('id', 'combat_desc')
            .attr('class', 'modal-header').appendTo(boxContent);

        var boxBody = $('<div>')
            .attr('id', 'combat_characters')
            .attr('class', 'modal-body').appendTo(boxContent);

        var boxFooter = $('<div>')
            .attr('id', 'combat_commands')
            .attr('class', 'modal-footer').appendTo(boxContent);

        box.prependTo($("#popup_container"));
        box.modal({backdrop: "static"});

        this._current_target = null;
        this._finished = false;
        this._result = null;
        this._loot = null;
        this._skill_cd_time = {};
    
        webclient.doSetSizes();
    },

    displayGetObject: function(data) {
        this._loot = data;
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
        
        var box = $('#combat_box').html("");

        var boxDialog = $('<div>').attr('class', 'modal-dialog modal-lg').appendTo(box);
        var boxContent = $('<div>').attr('class', 'modal-content').appendTo(boxDialog);

        var boxHeader = $('<div>')
            .attr('id', 'combat_messages')
            .attr('class', 'modal-header').appendTo(boxContent);

        var boxBodyLoot = $('<div>')
            .attr('id', 'combat_loot')
            .attr('class', 'modal-body').appendTo(boxContent);

        var boxBodyResult = $('<div>')
            .attr('id', 'combat_result')
            .attr('class', 'modal-footer').appendTo(boxContent);

        var boxFooter = $('<div>')
            .attr('class', 'modal-footer').appendTo(boxContent);

        // object's info
        var content = "";
        var element = "";
        var count = 0;

        if (self._loot) {
            // add object's name
            try {
                var first = true;
                var accepted = self._loot["accepted"]
                for (var key in accepted) {
                    element = key + ": " + accepted[key] + "<br>";

                    if (first) {
                        content += LS("You got:") + "<br>";
                        first = false;
                    }
                    content += element;
                    count += 1;
                }
            }
            catch(error) {
            }

            try {
                var first = true;
                var rejected = self._loot["rejected"];
                for (var key in rejected) {
                    element = key + ": " + rejected[key] + "<br>";

                    if (first) {
                        if (count > 0) {
                            content += "<br>"
                        }
                        first = false;
                    }
                    content += element;
                    count += 1;
                }
            }
            catch(error) {
            }

            loot.html(content);
        }

        if (count == 0) {
            // get nothing
            var result = $('<center>').attr('id', 'combat_result')
            .css('line-height', '150px');

            if ("stopped" in self._result) {
                result.text("Combat stopped !");
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
                    result.text(LS("You win !"));
                }
                else {
                    result.text(LS("You lost !"));
                }
            }
            
            result.appendTo(boxHeader);
        }
        else {
            // get objects
            var result = $('<center>').attr('id', 'combat_result')
                                      .css('line-height', '20px');
            
            if ("stopped" in self._result) {
                result.text("Combat stopped !");
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
                    result.text(LS("You win !"));
                }
                else {
                    result.text(LS("You lost !"));
                }
            }
            
            result.appendTo(boxHeader);
        }

        var center = $('<center>');
        var button = $('<button>')
            .addClass('btn btn-default')
            .attr('type', 'button')
            .attr('id', 'button_center')
            .attr('onClick', 'combat.closeCombat()')
            .text('OK')
            .addClass('btn btn-primary');

        button.appendTo(center);
        center.appendTo(boxFooter);
    },

    closeCombat: function() {
        if ($('#popup_box').size() == 0) {
            $('.modal-backdrop').remove();
        }
        if($('#combat_box').size() > 0){
            $('#combat_box').remove();
            $('.modal-backdrop').remove();
        }
    },

    displayCombatInfo: function(data) {
        var desc = $('#combat_desc');
        desc.text(data.desc);
        
        var characters = $('#combat_characters');
        for (var i in data.characters) {
            var fighter = data.characters[i];
            var div = $('<div>').attr('id', 'fighter_' + fighter.dbref.slice(1))
                                .text(fighter.name)
                                .data('dbref', fighter.dbref);
            $('<div>').addClass('hp')
                      .attr('id', 'status_' + fighter.dbref.slice(1))
                      .text(fighter.hp + '/' + fighter.max_hp)
                      .appendTo(div);
            
            if (fighter.dbref == this._self_dbref) {
                div.addClass("fighter_self");
            }
            else {
                div.addClass("fighter_enemy");
                if (!this._current_target) {
                    this._current_target = fighter.dbref;
                }
            }
            
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
                    .css({'left': 20 + i * 80})
                    .text(command.name);

                button.append($("<div>").addClass('cooldown'));
                
                button.appendTo(content);
            }
            
            commands.html(content);
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
                        div.addClass("fighter_self");
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
        var key = data["skill"];
        var btn = $('#combat_btn_' + key);
        this.set_button_cd(btn, cd);
                
        var gcd = data["gcd"];
        $('#combat_btns').each(function(){
            combat.set_button_cd($(this), cd);
        });
    },

    set_button_cd: function(btn, cd) {
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

    is_in_combat: function() {
        return this._finished;
    },

    get_current_target: function() {
        return this._current_target;
    },
}