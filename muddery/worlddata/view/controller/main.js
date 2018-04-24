
showConent = function(url) {
    $("#content-frame").attr("src", url);
}

setFrameSize = function() {
	var box = $("#content-box");
	var frame = $("#content-frame");

    var win_width = $(window).innerWidth();
    var win_height = $(window).innerHeight();

    frame.innerWidth(win_width - 135);
    frame.height(0);
        
    var frame_body = frame[0].contentWindow.document.body;
    var frame_height = frame_body.scrollHeight
    
    if (frame_height > win_height) {
		frame.height(frame_height);
	}
	else {
		frame.height(win_height);
	}
}

function frameReady() {
	setFrameSize();
}


$(function(){
    $(window).on("resize", setFrameSize);

    $("#menu-box").on("click", "button", function(e) {
        var table = $(e.currentTarget).data("table");
        if (table) {
            showConent('views/common_table.html?table=' + table);
        }
    });
    
    $("#content-frame").on("load", frameReady);

    $(".panel-heading").on("click", function(e) {
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
    });
});
