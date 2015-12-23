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
        $('<header>')
            .attr('id', 'header')
            .append($('<center>').append($('<h5>').text(LS('Muddery Webclient'))))
            .appendTo(body);

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
                .attr('onclick', 'doConnect()')
                .text(LS('CONNECT')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_login')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("login")')
                .text(LS('LOGIN')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_register')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("register")')
                .text(LS('REGISTER')))
            .appendTo(ul);

        $('<li>')
            .attr('id', 'tab_scene')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("scene")')
                .text(LS('SCENE')))
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
            .text(LS('CHAR'))
            .append($('<span>')
                .addClass('caret'))
            .appendTo(tab_character);

        var popup_character = $('<ul>')
            .addClass('dropdown-menu')
            .appendTo(tab_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("infomation")')
                .text(LS('STATUS')))
            .appendTo(popup_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("inventory")')
                .text(LS('INVENTORY')))
            .appendTo(popup_character);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("skill")')
                .text(LS('SKILL')))
            .appendTo(popup_character);

        // tab quest
        $('<li>')
            .attr('id', 'tab_quest')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("quest")')
                .text(LS('QUEST')))
            .appendTo(ul);

        // tab map
        $('<li>')
            .attr('id', 'tab_map')
            .attr('role', 'presentation')
            .addClass('active')
            .css('display', 'none')
            .append($('<a>')
                .attr('onclick', 'map.showMap()')
                .text(LS('MAP')))
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
            .text(LS('SYS'))
            .append($('<span>')
                .addClass('caret'))
            .appendTo(tab_system);

        var popup_system = $('<ul>')
            .addClass('dropdown-menu')
            .appendTo(tab_system);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'webclient.showPage("command")')
                .text(LS('COMMAND')))
            .appendTo(popup_system);

        $('<li>')
            .append($('<a>')
                .attr('onclick', 'commands.doLogout()')
                .text(LS('LOGOUT')))
            .appendTo(popup_system);
    },
}


$(window).ready(function(){
    frame.create();
    webclient.showUnloginTabs();
    webclient.showPage("login");
    webclient.doSetSizes();
});
