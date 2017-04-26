/*
Muddery webclient (javascript component)
*/

var frame = {
    create : function() {
        var body = $('body');

        // create popup container
        $('<div>')
            .attr('id', 'popup_container')
            .addClass('container')
            .appendTo(body);

        // create header
        var header = $('<header>')
            .attr('id', 'header')
            .appendTo(body);

        var center = $('<center>')
            .appendTo(header);

        $('<h5>').text(LS('Muddery Webclient'))
            .attr('id', 'game_title')
            .appendTo(center);

        // create wrapper
        var wrapper = $('<div>')
            .attr('id', 'wrapper')
            .appendTo(body);

        var middle = $('<div>')
            .attr('id', 'middlewindow')
            .appendTo(wrapper);

        // prompt bar
        $('<div>')
            .attr('id', 'prompt_bar')
            .appendTo(middle);

        // message window
        var msg_panel = $('<div>')
            .addClass('panel')
            .addClass('panel-default')
            .appendTo(middle);

        $('<div>')
            .attr('id', 'msg_wnd')
            .addClass('panel-body')
            .appendTo(msg_panel);

        // tabs window
        var tab_panel = $('<div>')
            .addClass('panel')
            .addClass('panel-default')
            .appendTo(middle);

        var tab_content = $('<div>')
            .attr('id', 'tab_content')
            .addClass('panel-body')
            .appendTo(tab_panel);

        uimgr.connectBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.loginBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.registerBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.sceneBox()
            .css('display', 'none')
            .appendTo(tab_content);

        var information = $('<div>')
            .attr('id', 'box_infomation')
            .css('display', 'none')
            .appendTo(tab_content);

        var table = $('<table>')
            .css('width', '100%')
            .append($('<tr>')
                .append($('<td>')
                    .append(uimgr.statusBox()))
                .append($('<td>')
                    .append(uimgr.equipmentBox())))
            .appendTo(information);

        uimgr.inventoryBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.skillBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.questBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.speechBox()
            .css('display', 'none')
            .appendTo(tab_content);

        uimgr.commandBox()
            .css('display', 'none')
            .appendTo(tab_content);

        // create tabs
        var tab_panel = $('<div>')
            .attr('id', 'tab_bar')
            .appendTo(middle);

        var ul = $('<ul>')
            .attr('id', 'tab_pills')
            .addClass('nav')
            .addClass('nav-tabs')
            .appendTo(tab_panel);

        $('<li>')
            .attr('id', 'tab_connect')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'Evennia.connect()')
                .text(LS('Connect')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_login')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("login")')
                .text(LS('Login')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_register')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("register")')
                .text(LS('Register')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_scene')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("scene")')
                .text(LS('Scene')))
            .appendTo(ul);

        // character popup menu
        var tab_character = $('<li>')
            .attr('id', 'tab_character')
            .attr('role', 'presentation')
            .addClass('dropup')
            .css('display', 'none')
            .appendTo(ul);

        $('<a>')
            .attr('data-toggle', 'dropdown')
            .attr('role', 'button')
            .attr('aria-haspopup', 'true')
            .attr('aria-expanded', 'false')
            .addClass('dropdown-toggle')
            .text(LS('Char'))
            .append($('<span>')
                .addClass('caret'))
            .appendTo(tab_character);

        var popup_character = $('<ul>')
            .addClass('dropdown-menu')
            .appendTo(tab_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("infomation")')
                .addClass('first-dropdown-item')
                .text(LS('Status')))
            .appendTo(popup_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("inventory")')
                .addClass('dropdown-item')
                .text(LS('Inventory')))
            .appendTo(popup_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("skill")')
                .addClass('dropdown-item')
                .text(LS('Skill')))
            .appendTo(popup_character);
            
        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("quest")')
                .addClass('dropdown-item')
                .text(LS('Quest')))
            .appendTo(popup_character);

        // tab social
        var tab_social = $('<li>')
            .attr('id', 'tab_social')
            .attr('role', 'presentation')
            .addClass('dropup')
            .css('display', 'none')
            .appendTo(ul);

        $('<a>')
            .attr('data-toggle', 'dropdown')
            .attr('role', 'button')
            .attr('aria-haspopup', 'true')
            .attr('aria-expanded', 'false')
            .addClass('dropdown-toggle')
            .text(LS('Social'))
            .append($('<span>')
                .addClass('caret'))
            .appendTo(tab_social);

        var popup_social = $('<ul>')
            .addClass('dropdown-menu')
            .appendTo(tab_social);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("speech")')
                .addClass('first-dropdown-item')
                .text(LS('Say')))
            .appendTo(popup_social);

        // tab map
        $('<li>')
            .attr('id', 'tab_map')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'map.showMap()')
                .text(LS('Map')))
            .appendTo(ul);

        // character system menu
        var tab_system = $('<li>')
            .attr('id', 'tab_system')
            .attr('role', 'presentation')
            .addClass('dropup')
            .css('display', 'none')
            .appendTo(ul);

        $('<a>')
            .attr('data-toggle', 'dropdown')
            .attr('role', 'button')
            .attr('aria-haspopup', 'true')
            .attr('aria-expanded', 'false')
            .addClass('dropdown-toggle')
            .text(LS('Sys'))
            .append($('<span>')
                .addClass('caret'))
            .appendTo(tab_system);

        var popup_system = $('<ul>')
            .addClass('dropdown-menu')
            .appendTo(tab_system);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'commands.doLogout()')
                .addClass('first-dropdown-item')
                .text(LS('Logout')))
            .appendTo(popup_system);

        $('<li>')
            .append($('<a>')
                .attr('id', 'item_command')
                .attr('onclick', 'webclient.showPage("command")')
                .addClass('dropdown-item')
                .text(LS('Command')))
            .appendTo(popup_system);

        if (this.show_command_box) {
            $("#item_command").css("display", "");
        } else {
            $("#item_command").css("display", "none");
        }
    },
}


$(window).ready(function(){
    frame.create();
    webclient.showUnloginTabs();
    webclient.showPage("login");
    webclient.doSetSizes();
});
