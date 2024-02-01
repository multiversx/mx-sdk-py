from multiversx_sdk.wallet.libraries.bls_facade import BLSFacade


def test_generate_public_key():
    facade = BLSFacade()

    # With good input
    public_key = facade.generate_public_key(bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247"))
    assert public_key.hex() == "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"

    # With bad input
    public_key = facade.generate_public_key(bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd7742"))
    assert public_key.hex() == ""


def test_compute_message_signature():
    facade = BLSFacade()

    # With good input
    signature = facade.compute_message_signature(
        message=b"hello",
        private_key=bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247")
    )

    assert signature.hex() == "84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86"

    # With bad input (bad key)
    signature = facade.compute_message_signature(
        message=b"hello",
        private_key=bytes.fromhex("7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd7742")
    )

    assert signature.hex() == ""


def test_verify_message_signature():
    facade = BLSFacade()

    # With good input
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex("e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"),
        message=b"hello",
        signature=bytes.fromhex("84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")
    )

    assert ok == True

    # With altered signature
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex("e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"),
        message=b"hello",
        signature=bytes.fromhex("94fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")
    )

    # With altered message
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex("e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"),
        message=b"helloWorld",
        signature=bytes.fromhex("84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")
    )

    assert ok == False

    # With bad public key
    ok = facade.verify_message_signature(
        public_key=bytes.fromhex("badbad95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"),
        message=b"hello",
        signature=bytes.fromhex("84fd0a3a9d4f1ea2d4b40c6da67f9b786284a1c3895b7253fec7311597cda3f757862bb0690a92a13ce612c33889fd86")
    )

    assert ok == False


def test_generate_sign_and_verify():
    facade = BLSFacade()
    message = b"hello"

    private_key = facade.generate_private_key()
    public_key = facade.generate_public_key(private_key)
    signature = facade.compute_message_signature(message, private_key)
    ok = facade.verify_message_signature(public_key, message, signature)

    assert ok == True
