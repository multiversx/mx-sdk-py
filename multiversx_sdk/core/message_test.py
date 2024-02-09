from pathlib import Path

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.wallet.user_signer import UserSigner
from multiversx_sdk.wallet.user_verifer import UserVerifier

parent = Path(__file__).parent.parent
message_computer = MessageComputer()
alice = Address.new_from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")


def test_message_v1_serialize_for_signing():
    message = Message(
        data="test message".encode(),
        address=alice
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

    packed_message = message_computer.pack(message)
    assert packed_message == {
        "address": "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th",
        "message": "74657374",
        "signature": "7aff43cd6e3d880a65033bf0a1b16274854fd7dfa9fe5faa7fa9a665ee851afd4c449310f5f1697d348e42d1819eaef69080e33e7652d7393521ed50d7427a0e",
        "version": 1
    }

    unpacked_message = message_computer.unpack(packed_message)
    assert unpacked_message.address.to_bech32() == message.address.to_bech32()
    assert unpacked_message.data == message.data
    assert unpacked_message.signature == message.signature
    assert unpacked_message.version == message.version

    verifier = UserVerifier.from_address(unpacked_message.address)
    assert verifier.verify(message_computer.compute_bytes_for_verifying(unpacked_message), unpacked_message.signature)
