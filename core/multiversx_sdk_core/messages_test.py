

from multiversx_sdk_core.messages import ArbitraryMessage, MessageV1


def test_message_v1_serialize_for_signing():
    message = MessageV1.from_string("test message")
    serialized = message.serialize_for_signing()
    assert serialized.hex() == "2162d6271208429e6d3e664139e98ba7c5f1870906fb113e8903b1d3f531004d"


def test_arbitrary_message_serialize_for_signing():
    message = ArbitraryMessage.from_string("test message")
    serialized = message.serialize_for_signing()
    assert serialized == b"test message"
