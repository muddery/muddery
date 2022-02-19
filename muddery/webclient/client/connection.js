/*
Webclient library, Handle websocket messages.
*/

(function() {
    var Connection = {

        debug: true,
        initialized: false,
        open: false,
        websocket: null,
        wsurl: settings.wsurl,
        registered_events: {},

        init: function() {
            if (this.initialized) {
                // make it safe to call multiple times.
                return;
            }
            this.initialized = true;
            log('Connection initialized.')
        },

        // Connect to the server.
        // Re-establishes the connection after it is lost.
        //
        connect: function() {
            if (this.open) {
                // Already connected.
                return;
            }

            log('Websocket connecting ...');
            if (this.websocket) {
                if (!(this.websocket.readyState == websocket.CLOSED || this.websocket.readyState == websocket.CLOSING)) {
                    // The connection is already open.
                    return;
                }
            }

            this.websocket = new WebSocket(this.wsurl);

            // Handle Websocket open event
            this.websocket.onopen = function (event) {
                log('Websocket connected.');
                open = true;
                Connection.onOpen();
            };

            // Handle Websocket close event
            this.websocket.onclose = function (event) {
                Connection.onClose();
                open = false;
            };

            // Handle websocket errors
            this.websocket.onerror = function (event) {
                if (websocket.readyState === websocket.CLOSED) {
                    // only call if websocket was ever open at all.
                    log("Websocket failed.")
                    Connection.onError();
                    open = false;
                }
            };

            // Handle incoming websocket data [cmdname, args, kwargs]
            this.websocket.onmessage = function (event) {
                var data = event.data;
                log("Received: " + data);
                Connection.onMessage(data);
            };
        },

        // Send a message to the server.
        send: function (message) {
            if (!message) {
                return;
            }

            log("Send: " + message);
            this.websocket.send(message);
        },

        disconnect: function() {
            // tell the server this connection is closing (usually
            // tied to when the client window is closed). This
            // Makes use of a websocket-protocol specific instruction.
            this.send(JSON.stringify({"websocket_close": ""}));
            this.websocket.close();
            open = false;
        },

        /*
         {
            on_open: on open callback function,
            on_close: on close callback function,
            on_error: on error callback function,
            on_message: on message callback function,
         }
        */

        bindEvents: function(events) {
            for (var key in events) {
                this.registered_events[key] = events[key];
            }
        },

        onOpen: function() {
            if ("on_open" in this.registered_events) {
                this.registered_events["on_open"]();
            }
        },

        onClose: function() {
            if ("on_close" in this.registered_events) {
                this.registered_events["on_close"]();
            }
        },

        onError: function() {
            if ("on_error" in this.registered_events) {
                this.registered_events["on_error"]();
            }
        },

        onMessage: function(data) {
            if ("on_message" in this.registered_events) {
                this.registered_events["on_message"](data);
            }
        },

        isConnected: function() {
            return this.open;
        },

        state: function() {
            return this.websocket.state;
        },
    };

    window.Connection = Connection;
})();


// helper logging function (requires a js dev-console in the browser)
function log(message) {
    if (Connection.debug) {
        console.log(message);
    }
}
