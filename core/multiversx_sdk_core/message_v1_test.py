

from multiversx_sdk_core.message_v1 import MessageV1


def test_serialize_for_signing():
    message = MessageV1.from_string("test message")
    serialized = message.serialize_for_signing()
    assert serialized.hex() == "2162d6271208429e6d3e664139e98ba7c5f1870906fb113e8903b1d3f531004d"
