
// load scripts
!function() {
    var public_scripts = ("PUBLIC" in scripts_dict) ? scripts_dict["PUBLIC"] : [];
    
	var begin = window.location.pathname.lastIndexOf("/");
    var name = begin < 0 ? window.location.pathname : window.location.pathname.substr(begin + 1);
    var frame_scripts = (name in scripts_dict) ? scripts_dict[name] : [];
    var scripts = public_scripts.concat(frame_scripts);
    
	for (var i in scripts) {
		$("<script>").attr("src", scripts[i])
					 .attr("type", "text/javascript")
					 .appendTo($("body"));
	}
}();
