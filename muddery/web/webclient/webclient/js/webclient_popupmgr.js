/*
 Muddery webclient_popupmgr (javascript component)
 */

var popupmgr = {

    showShop : function() {
        var shop = data_handler.shop_data;
        popupmgr.doCloseShop();

        try {
            popupmgr.createBox(true)
                .attr('id', 'shop_box')
                .prependTo($('#popup_container'));

            var header = $('#popup_header')
                .addClass('shop-header');

            // shop's name
            var name = shop.name;
            if (name.length == 0) {
                // placeholder
                header.append($("<span>").html("&nbsp;"));
            }
            else {
                header.append($("<span>").text(name));
            }

            var body = $('#popup_body');

            // shop's icon
            if ("icon" in shop && shop["icon"]) {
                var url = settings.resource_location + shop["icon"];
                var icon = $("<center>")
                    .append($("<img>")
                        .attr("src", url)
                        .addClass("shop_icon"))
                    .appendTo(body);
            }

            // shop's desc
            var desc = text2html.parseHtml(shop["desc"]);
            uimgr.divEmpty(desc).appendTo(body);

            if (shop["goods"]) {
                body.append($("<div>").append(this.tableShopGoods(shop["goods"])));
            }
        }
        catch(error) {
            popupmgr.doCloseShop();
            console.error(error.message);
        }

        webclient.doSetPopupSize();
    },

    tableShopGoods : function(data) {
        var tableInventoryElement = $("<table>")
            .attr("class", "tab_shop");
        var tableHeadElement = $("<thead>").appendTo(tableInventoryElement);
        var tableHeadTRElement = $("<tr>").appendTo(tableHeadElement)
            .append($("<th>").text(LS("NAME")).addClass("shop_goods_name"))
            .append($("<th>").text(LS("PRICE")).addClass("shop_goods_price"))
            .append($("<th>").text(LS("DESC")));

        var tbodyElement = $("<tbody>").appendTo(tableInventoryElement);
        for (var i in data) {
            try {
                var obj = data[i];
                var trElement = $("<tr>").appendTo(tbodyElement);

                // object's icon and name
                var tdElement = $("<td>").appendTo(trElement);

                if ("icon" in obj && obj["icon"]) {
                	var url = settings.resource_location + obj["icon"];
					var icon = $("<center>")
						.append($("<img>")
							.attr("src", url)
							.addClass("inventory_icon"))
						.appendTo(tdElement);
				}

                var name = obj["name"];
                if (obj["number"] > 1) {
                    name += "×" + obj["number"];
                }

                var command = "commands.doShopGoodsLink('" + obj["dbref"] + "'); return false;";
                var aHrefElement = $("<a>").appendTo(tdElement)
                    .attr("href", "#")
                    .attr("onclick", command)
                    .attr("cmd_name", "look")
                    .attr("cmd_args", obj["dbref"])
                    .text(name);

				// object's price
                tdElement = $("<td>").append(obj["price"] + " " + obj["unit"])
                    .appendTo(trElement);

                // object's desc
                var desc = text2html.parseHtml(obj["desc"]);
                tdElement = $("<td>").append(desc)
                    .appendTo(trElement);
            }
            catch(error) {
            }
        }
        return tableInventoryElement;
    },

    showGoods : function(data) {
        popupmgr.doCloseShop();
        popupmgr.createBox(true, 'popupmgr.showShop()')
            .attr('id', 'popup_box')
            .prependTo($("#popup_container"));

        // add object's name
        var title = text2html.parseHtml(data["name"]);
        $('#popup_header').html(title);

        var page = $('#popup_body');
        var footer = $('#popup_footer');

        // object's info
        var element = "";

        // add object's dbref
        var dbref = "";
        if ("dbref" in data) {
            dbref = data["dbref"];
            page.data("dbref", dbref);
        }

        // add object's icon
        try {
			if ("icon" in data && data["icon"]) {
				var url = settings.resource_location + data["icon"];
				element = $("<center>")
							.append($("<img>")
								.attr("src", url)
								.addClass("obj_icon"))
							.appendTo(page);
			}
        }
        catch(error) {
        }

        // add object's desc
        element = text2html.parseHtml(data["desc"]);
        uimgr.divEmpty(element).appendTo(page);

        uimgr.divBR().appendTo(footer);

        // Purchase button.
        var command = [{"name":LS("Buy"),
                        "cmd":"buy",
                        "args":data["dbref"]}];
        uimgr.divObjectCmds(command).appendTo(footer);

        webclient.doSetPopupSize();
    },

    createBox : function(can_close_dialogue, close_command) {
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

        if (can_close_dialogue) {
            if (!close_command) {
                close_command = 'popupmgr.doCloseBox()';
            }
            dlgHeader.append($('<button>')
                .attr('type', 'button')
                .attr('data-dismiss', 'modal')
                .attr('onclick', close_command)
                .addClass('close')
                .html('&times;'));
        }

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

    doCloseShop : function() {
        if($('#shop_box').size()>0){
            $('#shop_box').remove();
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