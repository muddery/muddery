
var local_string = {
	language_list: {
    	"en-us": local_string_en_us,
    	"zh-cn": local_string_zh_cn,
    	"zh-tw": local_string_zh_tw,
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


!function() {
    local_string.setLanguage(settings.default_language);
}();