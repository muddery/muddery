
controller = {
    init: function() {
        this.bindEvents();
        window.parent.controller.setFrameSize();
    },

    bindEvents: function() {
        $("#apply-button").on("click", this.onApply);
    },

    onApply: function(e) {
        window.parent.controller.confirm("", "Apply changes?", controller.confirmApply);
    },

    confirmApply: function() {
        window.parent.controller.hideWaiting();
        window.parent.controller.showWaiting("", "Applying changes. Please wait the server to restart.");

        service.applyChanges(controller.applySuccess, controller.applyFailed);
    },

    applySuccess: function(data) {
        window.parent.controller.hideWaiting();
        window.parent.controller.notify("", "Apply success.");
    },

    applyFailed: function(code, message, data) {
        window.parent.controller.hideWaiting();
        window.parent.controller.notify("", "Apply failed: " + code + ": " + message);
    },
}

$(document).ready(function() {
    controller.init();
});

