
MudderyCrypto = function() {
	this.crypt = new JSEncrypt();
    this.getEncryptKey();
}

/*
 * Query encrypt key from the server.
 */
MudderyCrypto.prototype.getEncryptKey = function() {
    core.service.getEncryptKey(this.getEncryptKeySuccess, this.getEncryptKeyFailed);
}

MudderyCrypto.prototype.getEncryptKeySuccess = function(data) {
	core.crypto.crypt.setPublicKey(data);
}

MudderyCrypto.prototype.getEncryptKeyFailed = function(request, status) {
    alert(core.trans("An error occurred while setting up the client!"));
}

MudderyCrypto.prototype.encrypt = function(data) {
    return this.crypt.encrypt(data)
}
