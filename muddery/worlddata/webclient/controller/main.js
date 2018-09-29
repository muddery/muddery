
controller = {

    init: function() {
        this.login = false;
        this.status_interval_id = 0;
        this.bindEvents();
    },

    bindEvents: function() {
        $(window).on("resize", this.onResize);

        $("#button-login").on("click", this.onLogin);

        $("#button-logout").on("click", this.onLogout);

        $("#menu-box").on("click", "button", this.onLeftMenu);
        
        $("#content-frame").on("load", this.onContentLoad);

        $(".panel-heading").on("click", this.onMenuPanel);

        $("#apply-button").on("click", this.onApply);
    },

    onResize: function(e) {
        controller.setFrameSize();
    },

    onLogin: function(e) {
        var username = $("#username").val();
        var password = $("#password").val();
        service.login(username, password, controller.loginSuccess, controller.loginFailed);
    },

    onLogout: function(e) {
        service.logout(controller.logoutSuccess, controller.logoutSuccess);
    },

    onLeftMenu: function(e) {
        var name = $(this).text();
        var table = $(this).data("table");
        var editor = $(this).data("editor");
        var page = $(this).data("page");
        var url = "";

        if (table) {
            // Set table editor.
            url = "common_table.html?table=" + table + "&editor=" + editor;
        }
        else if (page) {
            // Set actions page.
            url = page + ".html";
        }

        controller.setPage(name, url, 0);
    },

    onMenuPanel: function(e) {
        if ($(this).find("span").hasClass("glyphicon-chevron-up")) {
            $(this).find("span").toggleClass("glyphicon-chevron-down");
            $(this).find("span").toggleClass("glyphicon-chevron-up");
        }
        else {
            $("#menu-box").find(".glyphicon-chevron-up")
                .removeClass("glyphicon-chevron-up")
                .addClass("glyphicon-chevron-down");
            $("#menu-box").find(".panel-collapse")
                .removeClass("in");

            $(this).find("span").toggleClass("glyphicon-chevron-down");
            $(this).find("span").toggleClass("glyphicon-chevron-up");
        }
    },

    onApply: function(e) {
        controller.confirm("", "Apply changes?", controller.confirmApply);
    },

    onContentLoad: function(e) {
        controller.setFrameSize();
    },

    loginSuccess: function(data) {
        this.login = true;

        $("#username").val("");
        $("#password").val("");
        $("#login-message").text(" ");

        $("#login-view").hide();
        $("#editor-view").show();
    },

    loginFailed: function(code, message) {
        $("#login-message").text(message);
    },

    logoutSuccess: function(data) {
        this.login = false;
        $("#editor-view").hide();
        $("#login-view").show();
    },

    setFrameSize: function() {
	    var box = $("#content-box");
	    var frame = $(".content-frame:visible");
        if (frame.length == 0)  {
            return;
        }

        var win_width = $(window).innerWidth();
        var win_height = $(window).innerHeight();

        frame.innerWidth(win_width - 135);
        frame.height(0);
            
        var frame_body = frame[0].contentWindow.document.body;
        var frame_height = frame_body.scrollHeight + 1;
        
        if (frame_height > win_height) {
		    frame.height(frame_height);
	    }
	    else {
		    frame.height(win_height);
	    }
    },

    setPage: function(name, url, level) {
        // Set navigate bar.
        var selector = ">";
        if (level > 0) {
            selector += ":gt(" + (level - 1) + ")";
        }
        $("#navigate-bar" + selector).remove();
        $("#navigate-bar>").removeClass("active");

        var tab = $("<li>")
            .addClass("active")
            .append($("<a>")
                .attr("href", "javascript:void(0)")
                .attr("data-toggle", "tab")
                .text(name)
                .on('show.bs.tab', controller.onTabSelected));
        $("#navigate-bar").append(tab);

        // Add page.
        $("#contents" + selector).remove();
        $("#contents>").hide();

        $("<iframe>")
            .addClass("content-frame")
            .attr("src", url)
            .appendTo($("#contents"));

        this.setFrameSize();
    },

    pushPage: function(name, url) {
        // Set navigate bar.
        $("#navigate-bar>").removeClass("active");

        var tab = $("<li>")
            .addClass("active")
            .append($("<a>")
                .attr("href", "javascript:void(0)")
                .attr("data-toggle", "tab")
                .text(name)
                .on('show.bs.tab', controller.onTabSelected));
        $("#navigate-bar").append(tab);

        // Add page.
        $("#contents>").hide();

        $("<iframe>")
            .addClass("content-frame")
            .attr("src", url)
            .appendTo($("#contents"));

        this.setFrameSize();
    },

    // Pop last page.
    popPage: function(refresh) {
        $("#navigate-bar>:last").remove();
        $("#contents>:last").remove();

        $("#navigate-bar>:last").addClass("active");
        $("#contents>:last").show();

        if (refresh) {
            try {
                var c = $("#contents>:last")[0];
                var w = c.contentWindow;
                var t = w.controller;
                $("#contents>:last")[0].contentWindow.controller.refresh();
            }
            catch(e) {
            }
        }
    },

    onTabSelected: function(e) {
        // Do not act.
        e.preventDefault();
    },

    editRecord: function(editor_type, table_name, record_id, args) {
        var name = "";
        var url = "";
        if (editor_type == "object") {
            url = "object_editor.html?table=" + table_name;
        }
        else if (editor_type == "event") {
            url = "event_editor.html?table=" + table_name;
        }
        else if (editor_type == "event_action") {
            url = "event_action_editor.html?table=" + table_name;
        }
        else if (editor_type == "dialogue") {
            url = "dialogue_editor.html?table=" + table_name;
        }
        else if (editor_type == "sentence") {
            url = "dialogue_sentence_editor.html?table=" + table_name;
        }
        else {
            url = "common_editor.html?table=" + table_name;
        }

        if (record_id) {
            name = "Edit " + table_name;
            url += "&record=" + record_id;
        }
        else {
            name = "Add " + table_name;
        }

        if (args) {
            for (key in args) {
                url += "&" + key + "=" + args[key];
            }
        }

        controller.pushPage(name, url);
    },

    confirmApply: function() {
        service.applyChanges(controller.applySuccess, controller.applyFailed);
        controller.showWaiting("", "Applying changes. Please wait.");
    },

    applySuccess: function(data) {
        controller.showWaiting("", "Changes Applied. Please wait the server to restart.");
        controller.checkStatus();
        controller.status_interval_id = window.setInterval("controller.checkStatus()", 3000);
    },

    applyFailed: function(code, message, data) {
        controller.notify("", "Apply failed: " + code + ": " + message);
    },

    checkStatus: function() {
        service.checkStatus(controller.checkStatusSuccess);
    },

    checkStatusSuccess: function(data) {
        window.clearInterval(controller.status_interval_id);
        controller.notify("", "The server restarted.");
    },

    //////////////// Confirm Model ////////////////

    confirm: function(title, content, callback, data) {
        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").show();
        $("#cancel-button").show();
        $("#confirm-button").show();

        if (callback) {
            $("#confirm-button").one("click", data, callback);
        }
        else {
            $("#confirm-button").one("click", this.hideWaiting);
        }

        $("#confirm-dialog").modal();
    },

    notify: function(title, content, callback, data) {
        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").show();
        $("#cancel-button").hide();
        $("#confirm-button").show();

        if (callback) {
            $("#confirm-button").one("click", data, callback);
        }
        else {
            $("#confirm-button").one("click", this.hideWaiting);
        }

        $("#confirm-dialog").modal();
    },

    showWaiting: function(title, content) {
        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").hide();
        $("#cancel-button").hide();
        $("#confirm-button").hide();

        $("#confirm-dialog").modal();
    },

    hideWaiting: function() {
        $("#confirm-dialog").modal("hide");
    },
}

$(document).ready(function() {
    controller.init();
});
