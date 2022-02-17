
MudderyService = function() {
}

MudderyService.prototype = {

    getData: function(path, callback_success, callback_failed) {
        var url = window.location.origin + "/"+ path;
        $.ajax({
            url: url,
            type: "GET",
            cache: false,
            success: callback_success,
            error: callback_failed
        });
    },

    getEncryptKey: function(callback_success, callback_failed) {
        this.getData("keys/rsa_public.pem", callback_success, callback_failed);
    },
}


