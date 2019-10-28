
MudderyLocalString = function() {
}

MudderyLocalString.prototype = {

	language_list: {
    	"en-us": MudderyLocalStringEnUs,
    	"zh-cn": MudderyLocalStringZhCn,
	},

	language_code: "",

	local_string_dict: {},
	
	setLanguage: function(language) {
		if (this.language_code == language) {
			return false;
		}
		
		this.language_code = language;
		
	    if (language in this.language_list) {
            this.local_string_dict = this.language_list[language];
        }
        else {
            this.local_string_dict = {};
        }
        
        return true;
	},

	translate: function(str) {
		if (str in this.local_string_dict) {
        	return this.local_string_dict[str];
    	}

    	return str;
	},
}
