
function getQueryString(name) { 
	var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
    var args = window.location.search.substr(1);
    if (args.substr(-1) == "/") {
        args = args.substr(0, args.length - 1);
    }
    
	var r = args.match(reg); 
	if (r != null) {
	 	return unescape(r[2]);
	}
	return null; 
}
