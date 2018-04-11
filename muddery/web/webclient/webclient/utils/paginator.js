
/*
 * Paginate table rows.
 *
 * With ideas from 大宝.
 */

/*
 * wrapper: a wrapper contains the table. 
 * height: table row's max height.
 */
function Paginator(wrapper, height) {
	this.pages = [[]];
	this.current_page = 0;
	this.index_neighbours = 3;

    if (typeof(wrapper) === "string") {
        this.wrapper = document.querySelector(wrapper);
    }
    else {
        this.wrapper = wrapper;
    }
    
    this.table = this.wrapper.querySelector("table");

    this.page_index = document.createElement("div");
    this.page_index.id = "page_index";
    this.wrapper.appendChild(this.page_index);

    this.table_height = height ? height : 0;

    this.refresh();
}

Paginator.prototype = {

    refresh: function(height) {
        this.tbody = this.table.querySelector("tbody");
        this.trows = this.tbody.querySelectorAll("tr:not(.template)");
        
        if (height) {
            this.table_height = height;
        }

        this.setPages();
	    this.setPageIndex(1);
    },

    tableHeight: function(height) {
    	this.table_height = height;
    	this.setPages();
    },

    setPages: function() {
        var header_height = this.table.querySelector("thead").offsetHeight;
        var footer_height = this.page_index.clientHeight;
        var fixed_height = header_height + footer_height;
        
        var page_number = 0;
        this.pages = [[]];
        if (this.trows) {
        	for (var i = 0; i < this.trows.length; i++) {
            	if (!this.trows[i].parentNode) {
	            	this.tbody.appendChild(this.trows[i]);
	        	}
        	}
        
            var total_height = 0;
            for (var i = 0; i < this.trows.length; i++) {
                var row_height = this.trows[i].offsetHeight;

                if (this.pages[page_number].length == 0) {
                    this.pages[page_number].push(i);
                    total_height = fixed_height + row_height;
                    continue;
                }

                if (total_height + row_height > this.table_height) {
                    this.pages.push([i]);
                    page_number++;
                    total_height = fixed_height + row_height;
                }
                else {
                    this.pages[page_number].push(i);
                    total_height += row_height;
                }
            }
        }

        this.current_page = 0;
        this.gotoPage(1);
    },

    gotoPage: function(page) {
        if (this.current_page == page) {
        	return;
        }
        
        if (this.trows.length == 0) {
            return;
        }

        if (page < 1 || page > this.pages.length) {
            return;
        }
        
        this.current_page = page;
        
        // remove all rows
        for (var i = 0; i < this.trows.length; i++) {
            if (this.trows[i].parentNode) {
	            this.tbody.removeChild(this.trows[i]);
	        }
        }

		// add this page's rows
		for (var i in this.pages[page - 1]) {
			var row = this.pages[page - 1][i];
            this.tbody.appendChild(this.trows[row]);
        }

        // page index
        this.page_index.style.marginTop = "0";

        this.setPageIndex(page);

        // margin height
        var table_height = this.table.offsetHeight;
        var footer_height = this.page_index.clientHeight;
        var height = this.table_height - table_height - footer_height;
        if (height < 0) {
        	height = 0;
        }
        this.page_index.style.marginTop = height + "px";
    },
    
    setPageIndex: function(page) {
        // clear content
        this.page_index.textContent = "";
        
        if (this.pages.length == 1) {
            return;
        }
    
		// fixed indexes
        if (page > 1) {
			this.appendIndexLink("<<");
			this.page_index.appendChild(this.getSpace());
			
			this.appendIndexLink("<");
			this.page_index.appendChild(this.getSpace());
		}
		else {
			this.appendIndexText("<<");
			this.page_index.appendChild(this.getSpace());
			
			this.appendIndexText("<");
			this.page_index.appendChild(this.getSpace());
		}
		
		// add page indexes
		if (page <= this.pages.length) {
		    var begin = page - this.index_neighbours;
		    var end = page + this.index_neighbours;
		    if (begin < 1) {
		    	begin = 1;
		    	end = 1 + this.index_neighbours * 2;
		    }
		    if (end > this.pages.length) {
		    	end = this.pages.length;
		    	if (end - this.index_neighbours * 2 > 1) {
		    	    begin = end - this.index_neighbours * 2;
		    	}
		    	else {
		    	    begin = 1;
		    	}
		    }
		    
		    for (var i = begin; i <= end; i++) {
		        if (i != page) {
		            this.appendIndexLink(i);
		        }
				else {
					this.appendIndexText(i);
				}
				
				this.page_index.appendChild(this.getSpace());
		    }
		}
		
		// fixed indexes
		if (page < this.pages.length) {
			this.appendIndexLink(">");
			this.page_index.appendChild(this.getSpace());
			
			this.appendIndexLink(">>");
		}
		else {
			this.appendIndexText(">");
			this.page_index.appendChild(this.getSpace());
			
			this.appendIndexText(">>");
		}
    },
    
    appendIndexText: function(text) {
    	var index_text = document.createElement("span");
		index_text.className = "page_index_link";
		index_text.textContent = text;
		this.page_index.appendChild(index_text);
    },
    
    appendIndexLink: function(text) {
    	var index_link = document.createElement("a");
		index_link.className = "page_index_link";
		index_link.textContent = text;
		index_link.addEventListener("click", this);
		this.page_index.appendChild(index_link);
    },
    
    getSpace: function() {
    	var space = document.createElement("span");
        space.innerHTML = "&nbsp;&nbsp;&nbsp;";
        return space;
    },
    
    handleEvent: function(event) {
		switch (event.type) {
			case "click":
			    this.onClick(event);
				break;
		}
	},

	onClick: function(event) {
	    var page = 1;
	    var text = event.currentTarget.textContent;
	    switch (text) {
	        case "<<":
	            page = this.current_page - 10;
	            break;
	        case "<":
	            page = this.current_page - 1;
	            break;
	        case ">":
	            page = this.current_page + 1;
	            break;
	        case ">>":
	            page = this.current_page + 10;
	            break;
	        default:
	            page = parseInt(text);
	            break;
	    }
	    
	    if (page > this.pages.length) {
	        page = this.pages.length;
	    }
	    if (page < 1) {
	        page = 1;
	    }
	    
	    this.gotoPage(page);
	},
}
