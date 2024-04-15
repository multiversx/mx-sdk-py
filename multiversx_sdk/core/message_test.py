from pathlib import Path

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.constants import SDK_PY_SIGNER, UNKNOWN_SIGNER
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_verifer import UserVerifier

parent = Path(__file__).parent.parent
message_computer = MessageComputer()
alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")


def test_message_v1_serialize_for_signing():
    message = Message(
        data="test message".encode()
    )
    serialized = message_computer.compute_bytes_for_signing(message)
    assert serialized.hex() == "2162d6271208429e6d3e664139e98ba7c5f1870906fb113e8903b1d3f531004d"


def test_sign_packed_message_and_verify_unpacked_message():
    message = Message(
        data="test".encode(),
        address=alice
    )

    signer = UserSigner.from_pem_file(parent / "testutils" / "testwallets" / "alice.pem")
    message.signature = signer.sign(message_computer.compute_bytes_for_signing(message))
    assert message.signature.hex() == "7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e"

    packed_message = message_computer.pack_message(message)
    assert packed_message == {
        "address": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "message": "74657374",
        "signature": "7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e",
        "version": 1,
        "signer": SDK_PY_SIGNER
    }

    unpacked_message = message_computer.unpack_message(packed_message)
    assert unpacked_message.address
    assert unpacked_message.address.to_bech32() == alice.to_bech32()
    assert unpacked_message.data == message.data
    assert unpacked_message.signature == message.signature
    assert unpacked_message.version == message.version

    verifier = UserVerifier.from_address(unpacked_message.address)
    assert verifier.verify(message_computer.compute_bytes_for_verifying(unpacked_message), unpacked_message.signature)


def test_unpack_legacy_message():
    legacy_message = {
        "address": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "message": "0x7468697320697320612074657374206d657373616765",
        "signature": "0xb16847437049986f936dd4a0917c869730cbf29e40a0c0821ca70db33f44758c3d41bcbea446dee70dea13d50942343bb78e74979dc434bbb2b901e0f4fd1809",
        "version": 1,
        "signer": "ErdJS"
    }
    message = message_computer.unpack_message(legacy_message)

    assert message.address
    assert message.address.to_bech32() == alice.to_bech32()
    assert message.data.decode() == "this is a test message"
    assert message.signature.hex() == "b16847437049986f936dd4a0917c869730cbf29e40a0c0821ca70db33f44758c3d41bcbea446dee70dea13d50942343bb78e74979dc434bbb2b901e0f4fd1809"
    assert message.version == 1
    assert message.signer == "ErdJS"


def test_unpack_message():
    packed_message = {
        "address": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "message": "0x7468697320697320612074657374206d657373616765",
        "signature": "0xb16847437049986f936dd4a0917c869730cbf29e40a0c0821ca70db33f44758c3d41bcbea446dee70dea13d50942343bb78e74979dc434bbb2b901e0f4fd1809"
    }

    message = message_computer.unpack_message(packed_message)
    assert message.address
    assert message.address.to_bech32() == alice.to_bech32()
    assert message.data.decode() == "this is a test message"
    assert message.signature.hex() == "b16847437049986f936dd4a0917c869730cbf29e40a0c0821ca70db33f44758c3d41bcbea446dee70dea13d50942343bb78e74979dc434bbb2b901e0f4fd1809"
    assert message.version == 1
    assert message.signer == UNKNOWN_SIGNER
