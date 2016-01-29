/*
Client Data Handler
*/

var worldeditor = {
    doPost: function(data) {
        var csrftoken = $.cookie("csrftoken");
        if (!csrftoken) {
            return;
        }

        if (!window.XMLHttpRequest) {
            return;
        }

        var xmlhttp = new XMLHttpRequest();

        if (xmlhttp.overrideMimeType) {
            xmlhttp.overrideMimeType("text/html");
        }

        url = window.location.href;

        xmlhttp.onreadystatechange = this.statechange;
        xmlhttp.open("POST", url, true);
        xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xmlhttp.send(data + "&csrfmiddlewaretoken=" + csrftoken);
    },

    statechange: function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                var response = this.responseText;
            }
            else if (this.status == 500) {
                var response = this.responseText;
            }
        }  
    }
};
