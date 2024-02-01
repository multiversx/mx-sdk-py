import os
from pathlib import Path

from multiversx_sdk.wallet.validator_keys import ValidatorSecretKey
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner
from multiversx_sdk.wallet.validator_verifier import ValidatorVerifier

testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"


def test_validator_secret_key_generate_public_key():
    assert ValidatorSecretKey.from_string("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247").generate_public_key().hex() == "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"


def test_sign_message():
    signer = ValidatorSigner.from_pem_file(testwallets / "validatorKey00.pem")
    message = b"hello"
    signature = signer.sign(message)
    assert signature.hex() == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"


def test_verify_message():
    verifier = ValidatorVerifier.from_string("e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208")

    message = b"hello"
    signature = bytes.fromhex("84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")

    assert verifier.verify(message, signature) == True

    invalid_signature = bytes.fromhex("94fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")
    assert verifier.verify(message, invalid_signature) == False


def test_pem_save():
    path = testwallets / "validatorKey00.pem"
    path_saved = path.with_suffix(".saved")

    with open(path) as f:
        content_expected = f.read().strip()

    pem = ValidatorPEM.from_file(path)
    pem.save(path_saved)

    with open(path_saved) as f:
        content_actual = f.read().strip()

    assert content_actual == content_expected
    os.remove(path_saved)
