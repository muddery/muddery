/*
 Muddery webclient_popupmgr (javascript component)
 */

var popupmgr = {
    showAlert : function(msg, button) {
        popupmgr.doCloseBox();
        popupmgr.createMessageBox();

        $('#popup_header').html("Alert");
        $('#popup_body').html(text2html.parseHtml(msg));

        var html_button = $('<button>')
            .attr('class', 'btn btn-default')
            .attr('type', 'button')
            .attr('data-dismiss', 'modal')
            .text(button)
            .attr('id', 'button_center')
            .attr('onClick', 'popupmgr.doCloseBox()');
        $('#popup_footer').html(html_button);

        webclient.doSetSizes();
    },

    showDialogue : function(dialogues) {
        popupmgr.doCloseDialogue();

        try {
            if (dialogues.length == 0) {
                return;
            }

            popupmgr.createDialogueBox();

            if (dialogues.length == 1) {
                var content = "";
                if (dialogues[0].speaker.length > 0) {
                    content += dialogues[0].speaker + ":<br>";
                }
                content += text2html.parseHtml(dialogues[0].content);

                $('#popup_header').html('Dialogue');
                $('#popup_body').html(content);

                var html_button = '<div><br></div>\
                <div>\
                <input type="button" id="button_center" value="';
                html_button += LS("NEXT");
                html_button += '" class="btn btn-default"';

                if ("npc" in dialogues[0]) {
                    html_button += ' npc="' + dialogues[0].npc + '"';
                }
                html_button += ' dialogue="' + dialogues[0].dialogue + '"';
                html_button += ' sentence="' + dialogues[0].sentence + '"';
                html_button += ' onClick="commands.doDialogue(this); return false;"/>\
                </div>'

                $('#popup_footer').html(html_button);
            }
            else {
                var content = "";
                if (dialogues[0].speaker.length > 0) {
                    content += dialogues[0].speaker + ":<br>";
                }

                for (var i in dialogues) {
                    content += '<a href="#" onclick="commands.doDialogue(this); return false;"';
                    content += ' npc="' + dialogues[i].npc + '"';
                    content += ' dialogue="' + dialogues[i].dialogue + '"';
                    content += ' sentence="' + dialogues[i].sentence + '"';
                    content += '">';
                    content += text2html.parseHtml(dialogues[i].content);
                    content += '</a><br>';
                }

                $('#popup_body').html(content);

                var html_button = '<div><br></div>\
                <div>\
                <center>\tton_center" value="SELECT ONE" class="btn btn-primary" />\
                </div>'
                $('#popup_footer').html(html_button);
            }
        }
        catch(error) {
            popupmgr.doCloseDialogue();
        }

        webclient.doSetSizes();
    },

    createMessageBox : function() {
        var win_h = $(window).innerHeight();

        var dlg = $('<div>').attr('id', 'popup_box');
        dlg.attr('class', 'modal');
        dlg.attr('style', 'display: block; padding-left: 15px;');
        dlg.attr('role', 'dialog');
        var dlgDialog = $('<div>').attr('class', 'modal-dialog modal-sm').appendTo(dlg);
        var dlgContent = $('<div>').attr('class', 'modal-content').appendTo(dlgDialog);

        var dlgHeader = $('<div>')
            .attr('class', 'modal-header').appendTo(dlgContent);
        dlgHeader.append($('<button>')
            .attr('type', 'button')
            .attr('class', 'close')
            .attr('data-dismiss', 'modal')
            .html('&times;'))
            .attr('onclick', 'popupmgr.doCloseBox()');
        dlgHeader.append($('<h4>')
            .attr('id', 'popup_header')
            .attr('class', 'modal-title'));

        var dlgBody = $('<div>')
            .attr('class', 'modal-body').appendTo(dlgContent)
            .append($('<p>').attr('id', 'popup_body'));

        var dlgFooter = $('<div>')
            .attr('id', 'popup_footer')
            .attr('class', 'modal-footer').appendTo(dlgContent);

        $("#popup_container").prepend(dlg);
        dlg.modal({backdrop: "static"});
        dlg.css('top', Math.abs(win_h-dlgDialog.outerHeight())>>1);
    },

    createDialogueBox : function() {
        var win_h = $(window).innerHeight();

        var dlg = $('<div>').attr('id', 'dialogue_box');
        dlg.attr('class', 'modal');
        dlg.attr('style', 'display: block; padding-left: 15px;');
        dlg.attr('role', 'dialog');
        var dlgDialog = $('<div>').attr('class', 'modal-dialog modal-sm').appendTo(dlg);
        var dlgContent = $('<div>').attr('class', 'modal-content').appendTo(dlgDialog);

        var dlgHeader = $('<div>')
            .attr('class', 'modal-header').appendTo(dlgContent);
        dlgHeader.append($('<h4>')
            .attr('id', 'popup_header')
            .attr('class', 'modal-title'));

        var dlgBody = $('<div>')
            .attr('class', 'modal-body').appendTo(dlgContent)
            .append($('<p>').attr('id', 'popup_body'));

        var dlgFooter = $('<div>')
            .attr('id', 'popup_footer')
            .attr('class', 'modal-footer').appendTo(dlgContent);

        $("#popup_container").prepend(dlg);
        dlg.modal({backdrop: "static"});
        dlg.css('top', Math.abs(win_h-dlgDialog.outerHeight())>>1);
    },

    doCloseBox : function() {
        if($('#popup_box').size()>0){
            $('#popup_box').remove();
            $('.modal-backdrop').remove();
        }
        webclient.doSetSizes();
    },

    doCloseDialogue : function() {
        if($('#dialogue_box').size()>0){
            $('#dialogue_box').remove();
            $('.modal-backdrop').remove();
        }
        webclient.doSetSizes();
    },

    doCloseCombat : function() {
        if($('#combat_box').size()>0){
            $('#combat_box').remove();
            $('.modal-backdrop').remove();
        }
        webclient.doSetSizes();
    },

    doCloseMap : function() {
        if($('#map_box').size()>0){
            $('#map_box').remove();
            $('.modal-backdrop').remove();
        }
        webclient.doSetSizes();
    },
}