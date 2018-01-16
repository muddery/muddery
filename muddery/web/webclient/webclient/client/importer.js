
// load scripts
!function() {
	var begin = window.location.pathname.lastIndexOf("/");
    var name = begin < 0 ? window.location.pathname : window.location.pathname.substr(begin + 1);
    if (name in frame_scripts) {
    	var scripts = frame_scripts[name];
    	for (var i in scripts) {
    	    $("<script>").attr("src", scripts[i])
    	                 .attr("type", "text/javascript")
    	                 .attr("defer", "defer")
    	                 .appendTo($("body"));
    	}
    }
}();
