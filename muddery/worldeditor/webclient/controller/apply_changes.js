
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
        controller.checkStatus();
        controller.status_interval_id = window.setInterval("controller.checkStatus()", 3000);
    },

    applyFailed: function(code, message, data) {
        window.parent.controller.hideWaiting();
        window.parent.controller.notify("", "Apply failed: " + code + ": " + message);
    },

    checkStatus: function() {
        service.checkStatus(controller.checkStatusSuccess);
    },

    checkStatusSuccess: function(data) {
        window.clearInterval(controller.status_interval_id);

        window.parent.controller.hideWaiting();
        window.parent.controller.notify("", "The server restarted.");
    },
}

$(document).ready(function() {
    controller.init();
});

