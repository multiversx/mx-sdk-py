import subprocess
import sys
from pathlib import Path

import pytest

from multiversx_sdk.wallet.libraries.bls_facade import BLSFacade

REPOSITORY_ROOT = Path(__file__).parent.parent.parent.parent
VALID_PRIVATE_KEY = bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")


def test_generate_public_key():
    facade = BLSFacade()

    # With good input
    public_key = facade.generate_public_key(
        bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
    )
    assert (
        public_key.hex()
        == "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )

    # With bad input
    public_key = facade.generate_public_key(
        bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd7742")
    )
    assert public_key.hex() == ""


def test_compute_message_signature():
    facade = BLSFacade()

    # With good input
    signature = facade.compute_message_signature(
        message=b"hello",
        private_key=bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247"),
    )

    assert (
        signature.hex()
        == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
    )

    # With bad input (bad key)
    signature = facade.compute_message_signature(
        message=b"hello",
        private_key=bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd7742"),
    )

    assert signature.hex() == ""


def test_verify_message_signature():
    facade = BLSFacade()

    # With good input
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex(
            "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        ),
        message=b"hello",
        signature=bytes.fromhex(
            "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
        ),
    )

    assert ok

    # With altered signature
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex(
            "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        ),
        message=b"hello",
        signature=bytes.fromhex(
            "94fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
        ),
    )

    assert not ok

    # With altered message
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex(
            "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        ),
        message=b"helloWorld",
        signature=bytes.fromhex(
            "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
        ),
    )

    assert not ok

    # With bad public key
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex(
            "badbad95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
        ),
        message=b"hello",
        signature=bytes.fromhex(
            "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"
        ),
    )

    assert not ok


def test_generate_sign_and_verify():
    facade = BLSFacade()
    message = b"hello"

    private_key = facade.generate_private_key()
    public_key = facade.generate_public_key(private_key)
    signature = facade.compute_message_signature(message, private_key)
    ok = facade.verify_message_signature(public_key, message, signature)

    assert ok


@pytest.mark.parametrize(
    "private_key",
    [bytes(32), bytes(33), bytes(32) + b"\x01", bytes(64)],
    ids=["zero-key", "zero-key-33-bytes", "zero-key-then-nonzero-byte", "zero-key-64-bytes"],
)
def test_generate_public_key_with_zero_key_does_not_crash_the_process(private_key: bytes):
    # For the zero key, the native library panics (nil pointer dereference) and kills the process.
    # Some builds (e.g. "libbls.so") only read the first 32 bytes, so longer keys starting with 32 zero bytes crash, as well.
    # Here, we use a subprocess, so that a regression fails this test (instead of crashing the whole test session).
    code = "import sys; from multiversx_sdk.wallet.libraries.bls_facade import BLSFacade; print(BLSFacade().generate_public_key(bytes.fromhex(sys.argv[1])).hex() or 'EMPTY')"
    result = subprocess.run(
        [sys.executable, "-c", code, private_key.hex()],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "EMPTY"


@pytest.mark.parametrize(
    "private_key",
    [
        bytes(32),
        bytes(33),
        bytes(32) + b"\x01",
        VALID_PRIVATE_KEY + bytes(1),
        VALID_PRIVATE_KEY + VALID_PRIVATE_KEY,
        VALID_PRIVATE_KEY[:-1],
        b"",
    ],
    ids=[
        "zero-key",
        "zero-key-33-bytes",
        "zero-key-then-nonzero-byte",
        "valid-key-then-byte",
        "valid-key-twice",
        "31-bytes",
        "empty",
    ],
)
def test_private_keys_with_bad_length_or_zero_are_rejected(private_key: bytes):
    # Some builds of the native library only read the first 32 bytes of the key, thus they would accept a valid key followed by other bytes.
    # The facade rejects all these keys by itself, so that the behaviour is the same on all platforms.
    facade = BLSFacade()

    assert facade.compute_message_signature(b"hello", private_key) == b""

    # Safe to call in-process for the keys that are not zero-prefixed (they can't crash the library).
    if any(private_key[:32]):
        assert facade.generate_public_key(private_key) == b""
