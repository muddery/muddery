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

        onOpen: null,
        onClose: null,
        onError: null,
        onMessage: null,

        init: function(opts) {
            if (this.initialized) {
                // make it safe to call multiple times.
                return;
            }
            this.initialized = true;
            this.connection = new WebsocketConnection();
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

            log('Connecting.');
            if (this.websocket) {
                if (!(this.websocket.readyState == websocket.CLOSED || this.websocket.readyState == websocket.CLOSING)) {
                    // The connection is already open.
                    return;
                }
            }

            this.websocket = new WebSocket(wsurl);

            // Handle Websocket open event
            websocket.onopen = function (event) {
                open = true;
                if (this.onOpen) {
                    this.onOpen();
                }
            };

            // Handle Websocket close event
            websocket.onclose = function (event) {
                if (this.onClose) {
                    this.onClose();
                }
                open = false;
            };

            // Handle websocket errors
            websocket.onerror = function (event) {
                if (websocket.readyState === websocket.CLOSED) {
                    // only call if websocket was ever open at all.
                    log("Websocket failed.")
                    if (this.onError) {
                        this.onError();
                    }

                    open = false;
                }
            };

            // Handle incoming websocket data [cmdname, args, kwargs]
            websocket.onmessage = function (event) {
                var data = event.data;
                if (this.onMessage) {
                    this.onMessage((data);
                }
            };
        },

        // Send a message to the server.
        send: function (message) {
            if (!message) {
                return;
            }

            console.log("Send: " + message);
            this.websocket.send(message);
        },

        disconnect: function() {
            // tell the server this connection is closing (usually
            // tied to when the client window is closed). This
            // Makes use of a websocket-protocol specific instruction.
            self.send(JSON.stringify({"websocket_close": ""}));
            self.websocket.close();
            open = false;
        }

        /*
         {
            on_open: on open callback function,
            on_close: on close callback function,
            on_error: on error callback function,
            on_message: on message callback function,
         }
        */
        bindEvents: function(events) {
            if ("on_open" in events) {
                this.onOpen = events["on_open"];
            }
            if ("on_close" in events) {
                this.onClose = events["on_close"];
            }
            if ("on_error" in events) {
                this.onError = events["on_error"];
            }
            if ("on_message" in events) {
                this.onMessage = events["on_message"];
            }
        }

        isConnected: function() {
            return this.open;
        }

        state: function() {
            return this.websocket.state;
        }
    };

    window.Connection = Connection;
})();


// helper logging function (requires a js dev-console in the browser)
function log() {
    if (Connection.debug) {
        console.log(JSON.stringify(arguments));
    }
}
