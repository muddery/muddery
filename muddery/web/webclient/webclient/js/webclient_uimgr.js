/*
Muddery webclient_uimgr (javascript component)
*/

var uimgr = {
    CONST_A_HREF_ONCLICK : "popupmgr.doCloseBox(); commands.doCommandLink(this); return false;",
    divEmpty : function(element, args) {
        var divEmptyElement = $("<div>");
        var element = arguments[0]?arguments[0]:"";
        var args = arguments[1]?arguments[1]:new Array();
        if(typeof(element) == 'string'){
            for(key in args){
                divEmptyElement.attr(key, args[key]);
            }
            divEmptyElement.html(element);
            return divEmptyElement;
        }
    },

    divBR : function() {
        var divElement = uimgr.divEmpty();
        var BRElement = $("<br>")
            .appendTo(divElement);
        return divElement;
    },

    aHref : function(href, onclick, name, args) {
        var aHrefElement = $("<a>")
            .attr("href", href)
            .attr("onclick", onclick)
            .html(name);
        for(key in args){
            aHrefElement.attr(key, args[key]);
        }
        return aHrefElement;
    },

    divObjectCommon : function(obj_id, obj_title) {
        var divObjectCommonElement = uimgr.divEmpty()
            .attr("id", obj_id)
            .text(obj_title);
        return divObjectCommonElement;
    },

    divObjectCmds : function(data_cmds) {
        var divObjectCmdsElement = uimgr.divObjectCommon("object_cmds", LS("Actions") + LS(": "));
        // add cmds
        for (var i in data_cmds) {
            try {
                var cmd = data_cmds[i];

                var html_button = $('<button>')
                    .attr('class', 'btn btn-default')
                    .attr('type', 'button')
                    .attr('onclick', uimgr.CONST_A_HREF_ONCLICK)
                    .text(cmd['name'])
                    .attr("cmd_name", cmd["cmd"])
                    .attr("cmd_args", cmd["args"]);
                html_button.appendTo(divObjectCmdsElement);

                //var aHrefElement = uimgr.aHref("#", uimgr.CONST_A_HREF_ONCLICK, cmd["name"],
                //    {"cmd_name": cmd["cmd"], "cmd_args": cmd["args"], "style":"margin-left:10px;"});
                //aHrefElement.appendTo(divObjectCmdsElement);
            }
            catch(error) {
            }
        }
        return divObjectCmdsElement;
    },

    connectBox: function() {
        var box = $('<div>')
            .attr('id', 'box_connect');

        $('<div>')
            .text(LS('Please connect to the server.'))
            .appendTo(box);

        return box;
    },

    speechBox: function() {
        var box = $('<div>')
            .attr('id', 'box_speech');

        $('<div>')
            .text(LS('Please input your words.'))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'text')
                .attr('aria-describedby', 'basic-addon2')
                .attr('autocomplete', 'off')
                .attr('onkeydown', 'if (event.keyCode==13) {commands.doSay();}')
                .addClass('form-control')
                .addClass('inputbox')
                .val(''))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'button')
                .attr('autocomplete', 'off')
                .attr('onclick', 'commands.doSay()')
                .addClass('btn')
                .addClass('button_left')
                .val(LS('SEND')))
            .appendTo(box);

        return box;
    },
    
    commandBox: function() {
        var box = $('<div>')
            .attr('id', 'box_command');

        $('<div>')
            .text(LS('Please input command.'))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'text')
                .attr('aria-describedby', 'basic-addon2')
                .attr('autocomplete', 'off')
                .addClass('form-control')
                .addClass('inputbox')
                .val(''))
            .appendTo(box);

        $('<div>')
            .append($('<input>')
                .attr('type', 'button')
                .attr('autocomplete', 'off')
                .attr('onclick', 'commands.doSendCommand()')
                .addClass('btn')
                .addClass('button_left')
                .val(LS('SEND')))
            .appendTo(box);

        return box;
    },
}