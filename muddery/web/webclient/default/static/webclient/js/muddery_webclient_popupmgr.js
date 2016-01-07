/*
 Muddery webclient_popupmgr (javascript component)
 */

var popupmgr = {
    showAlert : function(msg, button) {
        popupmgr.doCloseBox();
        popupmgr.createBox()
            .attr('id', 'popup_box')
            .appendTo($('#popup_container'));

        $('#popup_header').text(LS('Message'));
        $('#popup_body').html(text2html.parseHtml(msg));

        var html_button = $('<button>')
            .attr('class', 'btn btn-default')
            .attr('type', 'button')
            .attr('data-dismiss', 'modal')
            .text(button)
            .attr('id', 'button_center')
            .attr('onClick', 'popupmgr.doCloseBox()');

        $('#popup_footer')
            .append($('<center>')
                .append(html_button));

        webclient.doSetPopupSize();
    },

    showDialogue : function(dialogues) {
        popupmgr.doCloseDialogue();

        try {
            if (dialogues.length == 0) {
                return;
            }

            popupmgr.createBox()
                .attr('id', 'dialogue_box')
                .prependTo($('#popup_container'));

            if (dialogues.length == 1) {
                var speaker = dialogues[0].speaker;
                if (speaker.length == 0) {
                    // placeholder
                    $('#popup_header')
                        .addClass('dialogue_header')
                        .html('&nbsp;');
                }
                else {
                    $('#popup_header')
                        .addClass('dialogue_header')
                        .text(speaker);
                }
                var content = text2html.parseHtml(dialogues[0].content);
                content = escape.parse(content, data_handler.getEscapes());
                $('#popup_body').html(content);

                var html_button = '<div><br></div>\
                <div>\
                <center>\
                <input type="button" value="';
                html_button += LS('Next');
                html_button += '" class="btn btn-default"';

                if ('npc' in dialogues[0]) {
                    html_button += ' npc="' + dialogues[0].npc + '"';
                }
                html_button += ' dialogue="' + dialogues[0].dialogue + '"';
                html_button += ' sentence="' + dialogues[0].sentence + '"';
                html_button += ' onClick="commands.doDialogue(this); return false;"/>\
                </center>\
                </div>';

                $('#popup_footer').html(html_button);
            }
            else {
                var speaker = dialogues[0].speaker;
                var content = "";
                for (var i in dialogues) {
                    content += '<a href="#" onclick="commands.doDialogue(this); return false;"';
                    content += ' npc="' + dialogues[i].npc + '"';
                    content += ' dialogue="' + dialogues[i].dialogue + '"';
                    content += ' sentence="' + dialogues[i].sentence + '"';
                    content += '">';

                    var string = text2html.parseHtml(dialogues[i].content);
                    string = escape.parse(string, data_handler.getEscapes());
                    content += string;
                    content += '</a><br>';
                }

                $('#popup_header').text(speaker);
                $('#popup_body').html(content);

                var html_button = '<div><br></div>\
                <div>\
                <center>\
                <input type="button" value="';
                html_button += LS('Select One');
                html_button += '" class="btn btn-default" />\
                </center>\
                </div>';

                $('#popup_footer').html(html_button);
            }
        }
        catch(error) {
            popupmgr.doCloseDialogue();
        }

        webclient.doSetPopupSize();
    },

    createBox : function() {
        var dlg = $('<div>')
            .attr('role', 'dialog')
            .css('display', 'block')
            .addClass('modal')
            .modal({backdrop: 'static'});

        var dlgDialog = $('<div>')
            .addClass('modal-dialog modal-sm')
            .addClass('vertical-center')
            .appendTo(dlg);

        var dlgContent = $('<div>')
            .addClass('modal-content')
            .appendTo(dlgDialog);

        var dlgHeader = $('<div>')
            .addClass('modal-header')
            .appendTo(dlgContent);

        dlgHeader.append($('<button>')
            .attr('type', 'button')
            .attr('data-dismiss', 'modal')
            .attr('onclick', 'popupmgr.doCloseBox()')
            .addClass('close')
            .html('&times;'));

        dlgHeader.append($('<h4>')
            .attr('id', 'popup_header')
            .addClass('modal-title'));

        var dlgBody = $('<div>')
            .addClass('modal-body')
            .append($('<p>')
                .attr('id', 'popup_body'))
            .appendTo(dlgContent);

        var dlgFooter = $('<div>')
            .attr('id', 'popup_footer')
            .addClass('modal-footer')
            .appendTo(dlgContent);

        return dlg;
    },

    doCloseBox : function() {
        if($('#popup_box').size()>0){
            $('#popup_box').remove();
            $('.modal-backdrop').remove();
        }
    },

    doCloseDialogue : function() {
        if($('#dialogue_box').size()>0){
            $('#dialogue_box').remove();
            $('.modal-backdrop').remove();
        }
    },

    doCloseCombat : function() {
        if($('#combat_box').size()>0){
            $('#combat_box').remove();
            $('.modal-backdrop').remove();
        }
    },

    doCloseMap : function() {
        if($('#map_box').size()>0){
            $('#map_box').remove();
            $('.modal-backdrop').remove();
        }
    },
}