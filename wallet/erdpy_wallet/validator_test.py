import os
from pathlib import Path

from erdpy_wallet.validator_signer import ValidatorSigner


def test_sign_message():
    os.environ["MCL_SIGNER_PATH"] = str(Path("~/elrondsdk/mcl_signer/v1.0.0/signer").expanduser())

    signer = ValidatorSigner.from_pem_file(Path("./erdpy_wallet/testdata/validatorKey00.pem"))
    message = DummyMessage(b"hello")
    signature = signer.sign(message)
    assert signature.hex() == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"


class DummyMessage:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def serialize_for_signing(self) -> bytes:
        return self.data
