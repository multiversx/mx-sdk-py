import os
from pathlib import Path

from erdpy_wallet.validator_pem import ValidatorPEM
from erdpy_wallet.validator_signer import ValidatorSigner


def test_sign_message():
    signer = ValidatorSigner.from_pem_file(Path("./erdpy_wallet/testdata/validatorKey00.pem"))
    message = DummyMessage(b"hello")
    signature = signer.sign(message)
    assert signature.hex() == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"


def test_pem_save():
    path = Path("./erdpy_wallet/testdata/validatorKey00.pem")
    path_saved = path.with_suffix(".saved")

    with open(path) as f:
        content_expected = f.read().strip()

    pem = ValidatorPEM.from_file(path)
    pem.save(path_saved)

    with open(path_saved) as f:
        content_actual = f.read().strip()

    assert content_actual == content_expected
    os.remove(path_saved)


class DummyMessage:
    def __init__(self, data: bytes) -> None:
        self.data = data

    def serialize_for_signing(self) -> bytes:
        return self.data
