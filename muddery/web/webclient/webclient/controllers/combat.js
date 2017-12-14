
var _ = parent._;
var parent_controller = parent.controller;
var text2html = parent.text2html;
var settings = parent.settings;
var commands = parent.commands;

var controller = {
	_self_dbref: "",
	_target: "",
	_interval_id: null,
	_timeout: 0,
	_timeline: 0,
	_combat_finished: true,
	_skill_cd_time: {},

    // on document ready
    onReady: function() {
        this.resetLanguage();
    },

	// reset view's language
	resetLanguage: function() {
	},

    // close popup box
    doClosePopupBox: function() {
        parent_controller.doClosePopupBox();
    },
    
    reset: function(skill_cd_time) {
		$("#desc").empty();
	
    	// Remove characters that are not template.
    	$("#characters>:not(.template)").remove();
    	
    	// Remove combat messages.
    	$("#messages>:not(.template)").remove();
    	
    	// Remove skill buttons that are not template.
    	$("#buttons>:not(.template)").remove();
    	
    	this._self_dbref = "";
    	this._target = "";
		this._combat_finished = false;
		this._skill_cd_time = skill_cd_time;
		if (this._interval_id != null) {
            this._interval_id = window.clearInterval(this._interval_id);
        }
    },

	setInfo: function(desc, timeout, characters, self_dbref) {
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

	    // add timeout
	    if (timeout > 0) {
	        var current_time = new Date().getTime();
	        this._timeout = timeout;
	        this._timeline = current_time + timeout * 1000;

	        $("#timeout").text(timeout);
	        $("#center_time").show();
	        this._interval_id = window.setInterval("refreshTimeout()", 1000);
	    }
	    else {
	        $("#timeout").empty();
	        $("#center_time").hide();
	    }
	    
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
           		item.find(".img_icon").attr("src", settings.resource_url + character["icon"]);
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
		var left = 10;
		var msg_box = $("#messages");
		var top = msg_box.position().top + msg_box.height() + 10;
        var line = 4;
        var width = 70;
        var line_height = 80;

		if (commands) {
            for (var i in commands) {
                var command = commands[i];
                
                var item = item_template.clone()
                    .removeClass("template")
                    .attr("id", "cmd_" + command["key"])
                    .data("key", command["key"])
                    .data("cd", 0)
                    .css({"left": left + i % line * width,
                          "top": top + parseInt(i / line) * line_height});
                    
                if (command["icon"]) {
                    item.find(".command_icon").attr("src", settings.resource_url + command["icon"]);
                }

                var name = text2html.parseHtml(command["name"]);
                item.find(".command_name").html(name);
                
                item.appendTo(container);
            }

            container.height(5 + parseInt((commands.length - 1) / line + 1) * line_height)
        }
    },

    setSkillResult: function(result) {
		if (this._combat_finished) {
			return;
		}
		
		if ("message" in result && result["message"]) {
		    var msg = text2html.parseHtml(result["message"]);
			this.displayMsg(msg);
		}
		
		if ("key" in result) {
			if (result.key == "skill_normal_hit" ||
				result.key == "skill_dunt") {

				var caller = $('#char_' + result.caller.slice(1));
				if (caller.hasClass("teammate")) {
					caller.animate({left: '50%'}, 100);
					caller.animate({left: '12%'}, 100);
				}
				else {
					caller.animate({right: '50%'}, 100);
					caller.animate({right: '12%'}, 100);
				}
			}
			else if (result.key == "skill_normal_heal" ||
					 result.key == "skill_powerful_heal") {
			}
			else if (result.key == "skill_escape") {
				if (result.effect == 1) {
					var item_id = "#char_" + result["target"].slice(1) + ".status";
					$(item_id).text(_("Escaped"));
				}
			}
		}
	
        // Update status.
        if ("status" in result) {
            this.updateStatus(result["status"]);
        }
    },
    
	// display a message in message window
	displayMsg: function(msg) {
        var msg_wnd = $("#messages");
        if (msg_wnd.length > 0) {
            msg_wnd.stop(true);
            msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
        }

		var item_template = msg_wnd.find("div.template");
		var item = item_template.clone()
			.removeClass("template")
			.addClass("msg-normal")
        	.html(msg)
            .appendTo(msg_wnd);

        // remove old messages
        var divs = msg_wnd.find("div:not(.template)");
        var max = 10;
        var size = divs.size();
        if (size > max) {
            divs.slice(0, size - max).remove();
        }
        
        // scroll message window to bottom
        msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
    },
    
    updateStatus: function(status) {
        for (var i in status) {
            var item_id = "#char_" + status[i]["dbref"].slice(1) + ">div.status";
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
        else {
            this._skill_cd_time[skill] = cd_time;
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
        if (key in this._skill_cd_time) {
            cd_time = this._skill_cd_time[key];
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
        button.data("cd", cd_time);
    },

    doCombatSkill: function(caller) {
        if (this._combat_finished) {
            return;
        }

        var key = $(caller).data("key");

        // Check CD.
        if (key in this._skill_cd_time) {
            var cd_time = this._skill_cd_time[key];
            var current_time = (new Date()).valueOf();
            if (cd_time > current_time) {
                return;
            }
        }

        commands.doCastSkill(key, this._target, true);
    },
    
    finishCombat: function(result) {
        this._combat_finished = true;
        if (this._interval_id != null) {
            this._interval_id = window.clearInterval(this._interval_id);
        }
    },
    
    isCombatFinished: function() {
        return this._combat_finished;
    },
};


function refreshTimeout() {
    var current_time = new Date().getTime();

    var remain = Math.ceil((controller._timeline - current_time) / 1000);
    if (remain > controller._timeout) {
        remain = controller._timeout;
    }
    if (remain < 0) {
        remain = 0;
    }

    $("#timeout").text(remain);
};


$(document).ready(function() {
	controller.onReady();
});