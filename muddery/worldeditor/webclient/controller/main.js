
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
        var page = $(this).data("page");
        var param_text = $(this).data("params");

        // set url
        if (!page) {
            console.error("No page data.");
            return;
        }
        var url = page + ".html";

        // Parse params
        if (param_text) {
            var url_params = "";
            var param_list = param_text.split(",");
            for (var i = 0; i < param_list.length; i++) {
                var key_value = param_list[i].split(":");
                if (key_value.length >= 2) {
                    if (url_params.length > 0) {
                        url_params += "&";
                    }
                    url_params += key_value[0] + "=" + key_value[1];
                }
            }

            if (url_params.length > 0) {
                url += "?" + url_params;
            }
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

    onContentLoad: function(e) {
        controller.setFrameSize();
    },

    loginSuccess: function(data) {
        this.login = true;
        service.set_token(data.token);

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
        if (frame_body) {
            var frame_height = frame_body.scrollHeight + 1;

            if (frame_height > win_height) {
                frame.height(frame_height);
            }
            else {
                frame.height(win_height);
            }
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

    pushPage: function(name, url, page_param) {
        if (page_param) {
            sessionStorage.page_param = JSON.stringify(page_param);
        }
        else {
            sessionStorage.page_param = "";
        }

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
    popPage: function(refresh, params) {
        $("#navigate-bar>:last").remove();
        $("#contents>:last").remove();

        $("#navigate-bar>:last").addClass("active");
        $("#contents>:last").show();

        if (refresh) {
            try {
                var c = $("#contents>:last")[0];
                var w = c.contentWindow;
                var t = w.controller;
                $("#contents>:last")[0].contentWindow.controller.refresh(params);
            }
            catch(e) {
            }
        }
    },

    onTabSelected: function(e) {
        // Do not act.
        e.preventDefault();
    },

    editRecord: function(editor_type, table_name, record_id, auto_key, args) {
        var name = "";
        var url = "";
        if (editor_type == "event") {
            url = "event_editor.html";
        }
        else if (editor_type == "element_event") {
            url = "element_event_editor.html";
        }
        else if (editor_type == "dialogue_event") {
            url = "dialogue_event_editor.html";
        }
        else if (editor_type == "event_action") {
            url = "event_action_editor.html";
        }
        else if (editor_type == "dialogue") {
            url = "dialogue_editor.html";
        }
        else {
            url = "common_editor.html";
        }

        if (table_name) {
            url += "?table=" + table_name
        }

        if (record_id) {
            name = "Edit " + table_name;
            url += "&record=" + record_id;
        }
        else {
            name = "Add " + table_name;
        }

        if (auto_key) {
            url += "&auto_key=1";
        }

        if (args) {
            for (key in args) {
                url += "&" + key + "=" + args[key];
            }
        }

        controller.pushPage(name, url, null);
    },

    editElement: function(base_element_type, element_type, element_key, no_delete) {
        var url = "element_editor.html?base_element_type=" + base_element_type + "&element_type=" + element_type;

        var name = "";
        if (element_key) {
            name = "Edit " + element_type;
            url += "&element_key=" + element_key;
            if (no_delete) {
                url += "&no_delete=1";
            }
        }
        else {
            name = "Add " + element_type;
        }

        controller.pushPage(name, url, null);
    },

    createElement: function(base_element_type, element_type, field_values) {
        var url = "element_editor.html?base_element_type=" + base_element_type + "&element_type=" + element_type;
        var name = "Add " + element_type;

        controller.pushPage(name, url, field_values);
    },

    editMatter: function(base_element_type, element_type, element_key, no_delete) {
        var url = "matter_editor.html?base_element_type=" + base_element_type + "&element_type=" + element_type;

        var name = "";
        if (element_key) {
            name = "Edit " + element_type;
            url += "&element_key=" + element_key;
            if (no_delete) {
                url += "&no_delete=1";
            }
        }
        else {
            name = "Add " + element_type;
        }

        controller.pushPage(name, url, null);
    },

    createMatter: function(base_element_type, element_type, field_values) {
        var url = "matter_editor.html?base_element_type=" + base_element_type + "&element_type=" + element_type;
        var name = "Add " + element_type;

        controller.pushPage(name, url, field_values);
    },

    editMap: function(map_key) {
        url = "map_editor.html";

        if (map_key) {
            name = "Edit MAP";
            url += "?map=" + map_key;
        }
        else {
            name = "Add MAP";
        }

        controller.pushPage(name, url, null);
    },

    editPropertiesDict: function(element_type, record_id) {
        var url = "properties_dict_editor.html?element_type=" + element_type;

        var name = "";
        if (record_id) {
            name = "编辑自定义属性";
            url += "&record=" + record_id;
        }
        else {
            name = "添加自定义属性";
        }

        controller.pushPage(name, url, null);
    },

    editElementProperties: function(element_type, element_key, level) {
        var url = "element_properties_editor.html?element_type=" + element_type + "&element_key=" + element_key;

        var name = "";
        if (level) {
            name = "编辑元素属性";
            url += "&level=" + level;
        }
        else {
            name = "添加元素属性";
        }

        controller.pushPage(name, url, null);
    },

    editConditionalDesc: function(element_type, element_key, record_id) {
        var url = "conditional_desc_editor.html?element_type=" + element_type + "&element_key=" + element_key;

        var name = "";
        if (record_id) {
            name = "编辑描述信息";
            url += "&record=" + record_id;
        }
        else {
            name = "添加描述信息";
        }

        controller.pushPage(name, url, null);
    },

    editQuest: function(element_key) {
        var url = "flow_editor.html";

        var name = "";
        if (element_key) {
            name = "Edit Quest";
            url += "?flow=" + element_key;
        }
        else {
            name = "Add Quest";
        }

        controller.pushPage(name, url, null);
    },

    //////////////// Confirm Model ////////////////
    confirm: function(title, content, callback, data) {
        if ($(".modal-backdrop").length > 0) {
            setTimeout(function() {
                controller.confirm(title, content, callback, data);
            }, 100);
            return;
        }

        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").show();
        $("#cancel-button").show();
        $("#confirm-button").show();

        $("#confirm-button").off("click");
        if (callback) {
            $("#confirm-button").one("click", data, callback);
        }
        else {
            $("#confirm-button").one("click", this.hideWaiting);
        }

        $("#confirm-dialog")
            .addClass("fade")
            .modal();
    },

    notify: function(title, content, callback, data) {
        if ($(".modal-backdrop").length > 0) {
            setTimeout(function() {
                controller.notify(title, content, callback, data);
            }, 100);
            return;
        }

        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").show();
        $("#cancel-button").hide();
        $("#confirm-button").show();

        $("#confirm-button").off("click");
        if (callback) {
            $("#confirm-button").one("click", data, callback);
        }
        else {
            $("#confirm-button").one("click", this.hideWaiting);
        }

        $("#confirm-dialog")
            .addClass("fade")
            .modal();
    },

    showWaiting: function(title, content) {
        if ($(".modal-backdrop").length > 0) {
            setTimeout(function() {
                controller.showWaiting(title, content);
            }, 100);
            return;
        }

        $("#confirm-title").text(title);
        $("#confirm-content").text(content);
        
        $("#close-button").hide();
        $("#cancel-button").hide();
        $("#confirm-button").hide();

        $("#confirm-dialog")
            .addClass("fade")
            .modal();
    },

    hideWaiting: function() {
        $("#confirm-dialog").modal("hide");
    },
}

$(document).ready(function() {
    controller.init();
});
