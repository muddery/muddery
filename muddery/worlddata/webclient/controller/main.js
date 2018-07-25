
controller = {
    init: function() {
        this.login = false;
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
        var table = $(this).data("table");
        var editor = $(this).data("editor");
        if (table) {
            controller.showTable(table, editor);
            return;
        }

        var page = $(this).data("page");
        if (page) {
            controller.showPage(page);
            return;
        }
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

    showTable: function(table_name, editor_type) {
        var url = "common_table.html?table=" + table_name + "&editor=" + editor_type;
 
        var table_box = $("#table-box");
        var editor_box = $("#editor-box");
        var page_box = $("#page-box");

        table_box.empty();

        $("<iframe>")
            .addClass("content-frame")
            .attr("src", url)
            .appendTo(table_box);

        editor_box.hide();
        page_box.hide();
        table_box.show();
        this.setFrameSize();
    },

    showTableView: function() {
        $("#editor-box").hide();
        $("#page-box").hide();
        $("#table-box").show();
    },

    showPage: function(page) {
        var url = page + ".html";
 
        var table_box = $("#table-box");
        var editor_box = $("#editor-box");
        var page_box = $("#page-box");

        page_box.empty();

        $("<iframe>")
            .addClass("content-frame")
            .attr("src", url)
            .appendTo(page_box);

        editor_box.hide();
        table_box.hide();
        page_box.show();
        this.setFrameSize();
    },

    editRecord: function(editor_type, table_name, record_id) {
        var url = "";
        if (editor_type == "object") {
            url = "object_editor.html?table=" + table_name;
        }
        else {
            url = "editor.html?table=" + table_name;
        }

        if (record_id) {
            url += "&record=" + record_id;
        }

        var table_box = $("#table-box");
        var editor_box = $("#editor-box");
        var page_box = $("#page-box");

        editor_box.empty();

        $("<iframe>")
            .addClass("content-frame")
            .attr("src", url)
            .appendTo(editor_box);

        table_box.hide();
        page_box.hide();
        editor_box.show();
        this.setFrameSize();
    },

    confirmApply: function() {
        service.applyChanges(controller.applySuccess, controller.applyFailed);
        controller.show_waiting("", "Applying changes. Please wait.");
    },

    applySuccess: function(data) {
        controller.notify("", "Changes Applied. Please wait the server to restart.");
    },

    applyFailed: function(code, message, data) {
        controller.notify("", "Apply failed: " + code + ": " + message);
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
            $("#confirm-button").one("click", this.hide_waiting);
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
            $("#confirm-button").one("click", this.hide_waiting);
        }

        $("#confirm-dialog").modal();
    },

    show_waiting: function(title, content) {
        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").hide();
        $("#cancel-button").hide();
        $("#confirm-button").hide();

        $("#confirm-dialog").modal();
    },

    hide_waiting: function() {
        $("#confirm-dialog").modal("hide");
    },
}

$(document).ready(function() {
    controller.init();
});

