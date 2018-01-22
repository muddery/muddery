//@ sourceURL=/controller/combat.js

/*
 * Derive from the base class.
 */
function MudderyCombat(root_controller) {
	BaseController.call(this, root_controller);
	
	this.self_dbref = "";
	this.target = "";
	this.interval_id = null;
	this.timeout = 0;
	this.timeline = 0;
	this.combat_finished = true;
	this.skill_cd_time = {};
}

MudderyCombat.prototype = prototype(BaseController.prototype);
MudderyCombat.prototype.constructor = MudderyCombat;

/*
 * Bind events.
 */
MudderyCombat.prototype.bindEvents = function() {
	this.onClick("#buttons", "button", this.onCombatSkill);
}

/*
 * Event when clicks a skill button.
 */
MudderyCombat.prototype.onCombatSkill = function(element) {
	if (this.combat_finished) {
		return;
	}

	var key = $(element).data("key");

	// Check CD.
	if (key in this.skill_cd_time) {
		var cd_time = this.skill_cd_time[key];
		var current_time = new Date().getTime();
		if (cd_time > current_time) {
			return;
		}
	}

	$$.commands.doCastSkill(key, this.target, true);
}
    
/*
 * Reset the combat box.
 */
MudderyCombat.prototype.reset = function(skill_cd_time) {
	$("#desc").empty();

	// Remove characters that are not template.
	this.clearElements("#characters");
	
	// Remove combat messages.
	this.clearElements("#messages");
	
	// Remove skill buttons that are not template.
	this.clearElements("#buttons");
	
	this.self_dbref = "";
	this.target = "";
	this.combat_finished = false;
	this.skill_cd_time = skill_cd_time;
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}
}

/*
 * Set combat data.
 */
MudderyCombat.prototype.setInfo = function(desc, timeout, characters, self_dbref) {
	if (this.combat_finished) {
		return;
	}
	
	this.self_dbref = self_dbref;
	
	var self_team = "";
	for (var i in characters) {
		if (characters[i]["dbref"] == self_dbref) {
			self_team = characters[i]["team"];
		}
	}
	
	// add desc
	$("#desc").html($$.text2html.parseHtml(desc));

	// add timeout
	if (timeout > 0) {
		var current_time = new Date().getTime();
		this.timeout = timeout;
		this.timeline = current_time + timeout * 1000;

		$("#timeout").text(timeout);
		$("#center_time").show();
		this.interval_id = window.setInterval("refreshTimeout()", 1000);
	}
	else {
		$("#timeout").empty();
		$("#center_time").hide();
	}
	
	// add characters
	var teammate_number = 0;
	var enemy_number = 0;
	var top = 10;
	var line_height = 30;
	
	var template = $("#characters>.template");
	for (var i in characters) {
		var character = characters[i];
		
		var item = this.cloneTemplate(template);
		item.attr("id", "char_" + character["dbref"].slice(1))
			.data("dbref", character["dbref"]);
		
		item.find(".status").text(character["hp"] + "/" + character["max_hp"]);
		
		if (character["icon"]) {
			item.find(".img_icon").attr("src", $$.settings.resource_url + character["icon"]);
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
			
			if (!this.target) {
				// Set default target.
				this.target = character["dbref"];
			}
		}
	}
}

/*
 * Set combat commands.
 */
MudderyCombat.prototype.setCommands = function(commands) {
	var template = $("#buttons>button.template");
	var left = 10;
	var msg_box = $("#messages");
	var top = msg_box.position().top + msg_box.height() + 10;
	var line = 4;
	var width = 70;
	var line_height = 80;

	if (commands) {
		for (var i in commands) {
			var command = commands[i];
			
			var item = this.cloneTemplate(template);
			item.attr("id", "cmd_" + command["key"])
				.data("key", command["key"])
				.data("cd", 0)
				.css({"left": left + i % line * width,
					  "top": top + parseInt(i / line) * line_height});
				
			if (command["icon"]) {
				item.find(".command_icon").attr("src", $$.settings.resource_url + command["icon"]);
			}

			item.find(".command_name").html($$.text2html.parseHtml(command["name"]));
		}

		$('#buttons').height(5 + parseInt((commands.length - 1) / line + 1) * line_height)
	}
}

/*
 * Set combat skill's result.
 */
MudderyCombat.prototype.setSkillResult = function(result) {
	if (this.combat_finished) {
		return;
	}
	
	if ("message" in result && result["message"]) {
		this.displayMsg($$.text2html.parseHtml(result["message"]));
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
				$(item_id).text($$("Escaped"));
			}
		}
	}

	// Update status.
	if ("status" in result) {
		this.updateStatus(result["status"]);
	}
}
    
/*
 * Display a message in message window.
 */
MudderyCombat.prototype.displayMsg = function(msg) {
	var msg_wnd = $("#messages");
	if (msg_wnd.length > 0) {
		msg_wnd.stop(true);
		msg_wnd.scrollTop(msg_wnd[0].scrollHeight);
	}

	var template = msg_wnd.find("div.template");
	var item = this.cloneTemplate(template);
	item.addClass("msg-normal")
		.html(msg);

	// remove old messages
	var divs = msg_wnd.find("div:not(.template)");
	var max = 10;
	var length = divs.length;
	if (length > max) {
		divs.slice(0, length - max).remove();
	}
	
	// scroll message window to bottom
	msg_wnd.animate({scrollTop: msg_wnd[0].scrollHeight});
}
    
/*
 * Update character's status.
 */
MudderyCombat.prototype.updateStatus = function(status) {
	for (var i in status) {
		var item_id = "#char_" + status[i]["dbref"].slice(1) + ">div.status";
		$(item_id).text(status[i]["hp"] + "/" + status[i]["max_hp"])
	}
}
    
/*
 * Set skill's CD.
 */
MudderyCombat.prototype.setSkillCD = function(skill, cd, gcd) {
	if (this.combat_finished) {
		return;
	}
	
	// update skill's cd
	var current_time = new Date().getTime();

	// cd_time in milliseconds
	var cd_time = current_time + cd * 1000;
	if (skill in this.skill_cd_time) {
		if (this.skill_cd_time[skill] < cd_time) {
			this.skill_cd_time[skill] = cd_time;
		}
	}
	else {
		this.skill_cd_time[skill] = cd_time;
	}

	var gcd_time = current_time + gcd * 1000;
	for (var key in this.skill_cd_time) {
		if (this.skill_cd_time[key] < gcd_time) {
			this.skill_cd_time[key] = gcd_time;
		}
	}

	// refresh button's CD
	$("#buttons>button").each(function() {
        controller.showButtonCD(this);
    });
}
    
/*
 * Show skill's CD.
 */
MudderyCombat.prototype.showButtonCD = function(button_id) {
	var button = $(button_id);
	var cooldown = button.find(">.cooldown");
	
	var key = button.data("key");

	var cd_time = 0;
	if (key in this.skill_cd_time) {
		cd_time = this.skill_cd_time[key];
	}

	var current_cd = button.data("cd");
	if (current_cd >= cd_time) {
		return;
	}

	var current_time = new Date().getTime();

	cooldown.stop(true, true);
	if (current_cd < current_time) {
		// set a new cd
		cooldown.css("height", "100%")
			.css("top", 0);
	}
	
	cooldown.animate({height: "0%", top: "100%"}, cd_time - current_time, "linear");
	button.data("cd", cd_time);
}

/*
 * Finish a combat.
 */
MudderyCombat.prototype.finishCombat = function(result) {
	this.combat_finished = true;
	if (this.interval_id != null) {
		this.interval_id = window.clearInterval(this.interval_id);
	}
}
    
/*
 * Finish a combat.
 */
MudderyCombat.prototype.isCombatFinished = function() {
    return this.combat_finished;
}

function refreshTimeout() {
    var current_time = new Date().getTime();

    var remain = Math.ceil((controller.timeline - current_time) / 1000);
    if (remain > controller.timeout) {
        remain = controller.timeout;
    }
    if (remain < 0) {
        remain = 0;
    }

    $("#timeout").text(remain);
};
