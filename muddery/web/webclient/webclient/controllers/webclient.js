
var controller = {

	showMessage: function(header, content, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_message";
        var controller = this.getFrameController(frame_id);
        controller.setPopup(header, content, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

	showObject: function(header, icon, content, commands) {
		this.doClosePopupBox();

        var frame_id = "#frame_object";
        var controller = this.getFrameController(frame_id);
        controller.setPopup(header, icon, content, commands);

        $(frame_id).show();
        $("#popup_container").show();
        webclient.doSetVisiblePopupSize();
	},

    // close popup box
    doClosePopupBox: function() {
		$("#popup_container").hide();
    	$("#popup_content").children().hide();
    },

    // show player's basic information
    setInfo: function(name, icon) {
        var controller = this.getFrameController("#frame_information");
        controller.setInfo(name, icon);
    },

    // show player's status
    setStatus: function(level, exp, max_exp, hp, max_hp, attack, defence) {
        var controller = this.getFrameController("#frame_information");
        controller.setStatus(level, exp, max_exp, hp, max_hp, attack, defence);
    },

    // show player's equipments
    setEquipments: function(equipments) {
        var controller = this.getFrameController("#frame_information");
        controller.setEquipments(equipments);
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

    getFrameController: function(frame_id) {
        var frame = $(frame_id);
        if (frame) {
            return frame[0].contentWindow.controller;
        }
    },
};
