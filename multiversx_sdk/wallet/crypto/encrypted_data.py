from typing import Any


class KeyDerivationParams:
    def __init__(self, n: int, r: int, p: int, dklen: int):
        # numIterations
        self.n = n
        # memFactor
        self.r = r
        # pFactor
        self.p = p
        self.dklen = dklen


class EncryptedData:
    def __init__(
        self,
        id: str,
        version: int,
        cipher: str,
        ciphertext: str,
        iv: str,
        kdf: str,
        kdfparams: KeyDerivationParams,
        salt: str,
        mac: str,
    ):
        self.id = id
        self.version = version
        self.cipher = cipher
        self.ciphertext = ciphertext
        self.iv = iv
        self.kdf = kdf
        self.kdfparams = kdfparams
        self.salt = salt
        self.mac = mac

    @classmethod
    def from_keyfile_object(cls, keyfile_object: dict[str, Any]) -> "EncryptedData":
        return cls(
            id=keyfile_object["id"],
            version=keyfile_object["version"],
            cipher=keyfile_object["crypto"]["cipher"],
            ciphertext=keyfile_object["crypto"]["ciphertext"],
            iv=keyfile_object["crypto"]["cipherparams"]["iv"],
            kdf=keyfile_object["crypto"]["kdf"],
            kdfparams=KeyDerivationParams(
                n=keyfile_object["crypto"]["kdfparams"]["n"],
                r=keyfile_object["crypto"]["kdfparams"]["r"],
                p=keyfile_object["crypto"]["kdfparams"]["p"],
                dklen=keyfile_object["crypto"]["kdfparams"]["dklen"],
            ),
            salt=keyfile_object["crypto"]["kdfparams"]["salt"],
            mac=keyfile_object["crypto"]["mac"],
        )
