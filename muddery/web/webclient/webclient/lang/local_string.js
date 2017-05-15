
var local_string = {
	language_list: {
    	"en-us": local_string_en_us,
    	"zh-cn": local_string_zh_cn,
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

function _(str) {
    return local_string.translate(str);
};
